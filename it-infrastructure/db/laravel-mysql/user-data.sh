#!/bin/bash
# Ubuntu 24.04 LTS. Код із Git, пароль лише з Secrets Manager.
set -Eeuo pipefail
umask 022
trap 'printf "Помилка розгортання в рядку %s\n" "$LINENO" >&2' ERR

REPO_URL="https://github.com/lisnayk/znu-lecture-examples.git"
GIT_REF="main"
APP_SUBDIR="it-infrastructure/db/laravel-mysql"
AWS_REGION="us-east-1"
DB_HOST="REPLACE_WITH_MYSQL_PROXY_ENDPOINT"
DB_SECRET_ARN="REPLACE_WITH_SECRET_ARN"
DB_DATABASE="infrastructure"
DB_CREATE_IF_MISSING="false"

[[ "$DB_HOST" != REPLACE_* && "$DB_SECRET_ARN" != REPLACE_* ]]
[[ "$AWS_REGION" =~ ^[a-z]{2}(-[a-z]+)+-[0-9]+$ ]]
[[ "$DB_HOST" =~ ^[A-Za-z0-9.-]+$ ]]
[[ "$DB_SECRET_ARN" =~ ^[A-Za-z0-9_!:/+=.@-]+$ ]]
[[ "$DB_SECRET_ARN" == arn:aws:secretsmanager:"$AWS_REGION":* ]]
[[ "$DB_DATABASE" =~ ^[A-Za-z0-9_-]{1,64}$ ]]
[[ "$DB_CREATE_IF_MISSING" == true || "$DB_CREATE_IF_MISSING" == false ]]
[[ "$REPO_URL" == https://* && "$GIT_REF" != -* && -n "$GIT_REF" ]]
[[ "$APP_SUBDIR" != /* && "$APP_SUBDIR" != *..* ]]
source /etc/os-release
[[ "$ID" == ubuntu && "$VERSION_ID" == 24.04 ]]
if [[ ! -f /etc/nginx/sites-available/ec2-laravel ]] && ss -H -ltn 'sport = :80' | grep -q .; then
  printf 'Порт 80 зайнятий. Використайте окремий EC2 для Laravel.\n' >&2
  exit 1
fi

export DEBIAN_FRONTEND=noninteractive GIT_TERMINAL_PROMPT=0
apt-get -o Acquire::Retries=3 update
apt-get -o Acquire::Retries=3 install -y nginx php8.3-fpm php8.3-cli php8.3-mysql \
  php8.3-mbstring php8.3-xml php8.3-curl php8.3-zip git curl unzip ca-certificates
systemctl stop nginx php8.3-fpm

BASE="/opt/ec2-laravel"
CHECKOUT="$BASE/repository"
mkdir -p "$BASE"
export COMPOSER_HOME="$BASE/.composer"
install -d -m 700 "$COMPOSER_HOME"
if [[ ! -e "$CHECKOUT" ]]; then
  git clone --depth 1 "$REPO_URL" "$CHECKOUT"
fi
[[ "$(git -C "$CHECKOUT" config --get remote.origin.url)" == "$REPO_URL" ]]
[[ -z "$(git -C "$CHECKOUT" status --porcelain)" ]]
git -C "$CHECKOUT" fetch --depth 1 origin "$GIT_REF"
git -C "$CHECKOUT" checkout --detach FETCH_HEAD
APP="$CHECKOUT/$APP_SUBDIR"
for file in artisan composer.json composer.lock start.sh deploy/migrate.service deploy/nginx.conf deploy/web-dependency.conf; do
  [[ -f "$APP/$file" ]]
done

curl --fail --silent --show-error --retry 3 https://getcomposer.org/installer -o "$BASE/composer-setup.php"
curl --fail --silent --show-error --retry 3 https://composer.github.io/installer.sig -o "$BASE/composer-setup.sig"
[[ "$(php -r "echo hash_file('sha384', '$BASE/composer-setup.php');")" == "$(cat "$BASE/composer-setup.sig")" ]]
php "$BASE/composer-setup.php" --install-dir="$BASE" --filename=composer.phar --quiet
rm -- "$BASE/composer-setup.php" "$BASE/composer-setup.sig"
cd "$APP"

if [[ -f .env ]]; then
  APP_KEY="$(sed -n 's/^APP_KEY=//p' .env)"
  [[ "$APP_KEY" =~ ^base64:[A-Za-z0-9+/=]+$ ]]
else
  APP_KEY="$(php -r 'echo "base64:".base64_encode(random_bytes(32));')"
fi
cat > .env <<EOF
APP_NAME="Каталог сервісів"
APP_ENV=production
APP_KEY=$APP_KEY
APP_DEBUG=false
APP_LOCALE=uk
APP_FALLBACK_LOCALE=uk
APP_MAINTENANCE_DRIVER=file
LOG_CHANNEL=single
LOG_LEVEL=warning
SESSION_DRIVER=file
CACHE_STORE=file
QUEUE_CONNECTION=sync
DB_CONNECTION=mysql
DB_AUTH_MODE=secrets
DB_HOST=$DB_HOST
DB_PORT=3306
DB_DATABASE=$DB_DATABASE
DB_CREATE_IF_MISSING=$DB_CREATE_IF_MISSING
DB_USERNAME=
DB_PASSWORD=
AWS_REGION=$AWS_REGION
DB_SECRET_ARN=$DB_SECRET_ARN
DB_SSL_CA=/etc/ssl/certs/ca-certificates.crt
EOF
chown root:www-data .env
chmod 640 .env
COMPOSER_ALLOW_SUPERUSER=1 php "$BASE/composer.phar" install --no-dev --no-interaction --prefer-dist --optimize-autoloader
mkdir -p storage/framework/cache/data storage/framework/sessions storage/framework/views storage/logs bootstrap/cache
chown -R www-data:www-data storage bootstrap/cache
chmod -R u+rwX,g+rX,o-rwx storage bootstrap/cache
ln -sfnT "$APP" "$BASE/current"
runuser -u www-data -- php artisan config:cache
runuser -u www-data -- php artisan view:cache

install -m 644 deploy/migrate.service /etc/systemd/system/ec2-laravel-migrate.service
for service in nginx php8.3-fpm; do
  mkdir -p "/etc/systemd/system/$service.service.d"
  install -m 644 deploy/web-dependency.conf "/etc/systemd/system/$service.service.d/ec2-laravel.conf"
done
install -m 644 deploy/nginx.conf /etc/nginx/sites-available/ec2-laravel
rm -f /etc/nginx/sites-enabled/default
ln -sfn /etc/nginx/sites-available/ec2-laravel /etc/nginx/sites-enabled/ec2-laravel
nginx -t
systemctl daemon-reload
systemctl enable ec2-laravel-migrate php8.3-fpm nginx
systemctl restart ec2-laravel-migrate
systemctl restart php8.3-fpm nginx
curl --fail --silent --show-error --retry 5 --retry-connrefused http://127.0.0.1/up >/dev/null
printf 'Laravel запущено. Відкрийте IP інстанса для перевірки CRUD.\n'
