#!/bin/bash
# Ubuntu 24.04. У user data є лише конфігурація, без пароля та AWS keys.
set -Eeuo pipefail
umask 022
trap 'printf "Помилка user data в рядку %s\n" "$LINENO" >&2' ERR

REPO_URL="https://github.com/lisnayk/znu-lecture-examples.git"
GIT_REF="main"
APP_SUBDIR="it-infrastructure/examples/ec2-rds-secrets"

AWS_REGION="eu-central-1"
DB_SECRET_ARN="REPLACE_WITH_FULL_SECRET_ARN"
DB_HOST="REPLACE_WITH_PROXY_ENDPOINT"
DB_TARGET="proxy"
DB_NAME="infrastructure"
DB_PORT="5432"

if [[ "$DB_SECRET_ARN" == REPLACE_* || "$DB_HOST" == REPLACE_* ]]; then
  printf 'Заповніть DB_SECRET_ARN і DB_HOST перед запуском EC2.\n' >&2
  exit 1
fi
for value in "$AWS_REGION" "$DB_SECRET_ARN" "$DB_HOST" "$DB_NAME" "$DB_PORT" "$DB_TARGET"; do
  [[ "$value" =~ ^[A-Za-z0-9_.:/@-]+$ ]] || { printf 'Некоректна конфігурація.\n' >&2; exit 1; }
done
[[ "$DB_SECRET_ARN" == arn:aws:secretsmanager:"$AWS_REGION":* ]]
[[ "$DB_PORT" =~ ^[0-9]+$ && "$DB_PORT" -ge 1 && "$DB_PORT" -le 65535 ]]
[[ "$DB_TARGET" == direct || "$DB_TARGET" == proxy ]]
[[ "$DB_TARGET" != proxy || "$DB_PORT" == 5432 ]]
[[ "$REPO_URL" == https://* && -n "$GIT_REF" && "$GIT_REF" != -* ]]
[[ "$APP_SUBDIR" != /* && "$APP_SUBDIR" != *..* && -n "$APP_SUBDIR" ]]

source /etc/os-release
[[ "$ID" == ubuntu && "$VERSION_ID" == 24.04 ]] || {
  printf 'Для цього сценарію потрібна Ubuntu 24.04 LTS.\n' >&2
  exit 1
}
export DEBIAN_FRONTEND=noninteractive GIT_TERMINAL_PROMPT=0
apt-get -o Acquire::Retries=3 update
apt-get -o Acquire::Retries=3 install -y python3 python3-venv git curl ca-certificates

BASE="/opt/ec2-rds-secrets"
CHECKOUT="$BASE/repository"
CONFIG="/etc/ec2-rds-secrets.env"
mkdir -p "$BASE"
if [[ ! -e "$CHECKOUT" ]]; then
  git clone --depth 1 "$REPO_URL" "$CHECKOUT"
fi
[[ "$(git -C "$CHECKOUT" config --get remote.origin.url)" == "$REPO_URL" ]]
[[ -z "$(git -C "$CHECKOUT" status --porcelain)" ]]
git -C "$CHECKOUT" fetch --depth 1 origin "$GIT_REF"
git -C "$CHECKOUT" checkout --detach FETCH_HEAD

APP="$CHECKOUT/$APP_SUBDIR"
for file in app.py requirements.txt ec2-rds-secrets.service static/index.html static/app.js static/style.css; do
  [[ -f "$APP/$file" ]] || { printf 'Немає %s/%s.\n' "$APP_SUBDIR" "$file" >&2; exit 1; }
done
python3 -m venv "$BASE/venv"
"$BASE/venv/bin/python" -m pip install --disable-pip-version-check -r "$APP/requirements.txt"
if [[ "$DB_TARGET" == proxy ]]; then
  # Proxy використовує ACM. Довіряємо актуальному системному CA bundle.
  install -m 644 /etc/ssl/certs/ca-certificates.crt "$BASE/db-ca-bundle.pem"
else
  curl --fail --silent --show-error --retry 3 \
    https://truststore.pki.rds.amazonaws.com/global/global-bundle.pem \
    -o "$BASE/db-ca-bundle.pem.new"
  install -m 644 "$BASE/db-ca-bundle.pem.new" "$BASE/db-ca-bundle.pem"
  rm "$BASE/db-ca-bundle.pem.new"
fi

printf '%s\n' \
  "AWS_REGION=$AWS_REGION" "DB_SECRET_ARN=$DB_SECRET_ARN" "DB_HOST=$DB_HOST" \
  "DB_NAME=$DB_NAME" "DB_PORT=$DB_PORT" "DB_TARGET=$DB_TARGET" "DB_SSLROOTCERT=$BASE/db-ca-bundle.pem" > "$CONFIG"
chmod 600 "$CONFIG"
ln -sfnT "$APP" "$BASE/current"
install -m 644 "$APP/ec2-rds-secrets.service" /etc/systemd/system/ec2-rds-secrets.service
systemctl daemon-reload
systemctl enable ec2-rds-secrets.service
systemctl restart ec2-rds-secrets.service

python3 - <<'PYCHECK'
import json
import time
from urllib.request import urlopen
for attempt in range(30):
    try:
        with urlopen("http://127.0.0.1/healthz", timeout=2) as response:
            assert json.load(response)["status"] == "ok"
        print("Вебзастосунок відповідає на порту 80.")
        print("Відкрийте сторінку для перевірки ролі, Secrets Manager і RDS.")
        break
    except (OSError, AssertionError):
        time.sleep(2)
else:
    raise SystemExit("Немає відповіді. Перевірте journalctl -u ec2-rds-secrets.")
PYCHECK
