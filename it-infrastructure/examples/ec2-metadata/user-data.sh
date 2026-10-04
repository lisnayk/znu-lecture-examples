#!/bin/bash
# EC2 user data. Застосунок завантажується з публічного Git-репозиторію.
# Репозиторій налаштовано. GIT_REF — гілка, тег або повний SHA коміту.
set -Eeuo pipefail
umask 022
trap 'printf "Помилка user data в рядку %s\n" "$LINENO" >&2' ERR

REPO_URL="https://github.com/lisnayk/znu-lecture-examples.git"
GIT_REF="main"
APP_SUBDIR="it-infrastructure/examples/ec2-metadata"

if [[ -z "$REPO_URL" ]]; then
  printf 'Заповніть REPO_URL перед запуском інстанса.\n' >&2
  exit 1
fi
case "$REPO_URL" in
  https://*) ;;
  *) printf 'Для цього демо потрібен публічний HTTPS Git URL.\n' >&2; exit 1 ;;
esac
if [[ -z "$GIT_REF" || "$GIT_REF" == -* || "$APP_SUBDIR" == /* || "$APP_SUBDIR" == *..* ]]; then
  printf 'Перевірте GIT_REF та відносний шлях APP_SUBDIR.\n' >&2
  exit 1
fi

source /etc/os-release
case "$ID" in
  ubuntu)
    export DEBIAN_FRONTEND=noninteractive
    apt-get -o Acquire::Retries=3 update
    apt-get -o Acquire::Retries=3 install -y python3 git ca-certificates
    ;;
  amzn)
    dnf install -y python3 git ca-certificates
    ;;
  *)
    printf 'Підтримуються Ubuntu та Amazon Linux. Отримано %s.\n' "$ID" >&2
    exit 1
    ;;
esac

export GIT_TERMINAL_PROMPT=0
BASE="/opt/ec2-metadata"
CHECKOUT="$BASE/repository"
mkdir -p "$BASE"
if [[ ! -e "$CHECKOUT" ]]; then
  git clone --depth 1 "$REPO_URL" "$CHECKOUT"
fi
# Повторний запуск не перезаписує сторонній репозиторій або локальні зміни.
[[ "$(git -C "$CHECKOUT" config --get remote.origin.url)" == "$REPO_URL" ]]
[[ -z "$(git -C "$CHECKOUT" status --porcelain)" ]]
git -C "$CHECKOUT" fetch --depth 1 origin "$GIT_REF"
git -C "$CHECKOUT" checkout --detach FETCH_HEAD

APP="$CHECKOUT/$APP_SUBDIR"
for file in app.py static/index.html static/style.css static/app.js ec2-metadata.service; do
  if [[ ! -f "$APP/$file" ]]; then
    printf 'У репозиторії немає %s/%s. Перевірте APP_SUBDIR.\n' "$APP_SUBDIR" "$file" >&2
    exit 1
  fi
done
/usr/bin/python3 -m py_compile "$APP/app.py"
ln -sfnT "$APP" "$BASE/current"
install -m 644 "$APP/ec2-metadata.service" /etc/systemd/system/ec2-metadata.service
systemctl daemon-reload
systemctl enable ec2-metadata.service
systemctl restart ec2-metadata.service

/usr/bin/python3 - <<'PYCHECK'
import json
import time
from urllib.request import urlopen

for attempt in range(30):
    try:
        with urlopen("http://127.0.0.1/healthz", timeout=2) as response:
            data = json.load(response)
        if data["status"] == "ok":
            print("Вебзастосунок відповідає на порту 80.")
            print("Стан IMDS:", data["metadata"])
            break
    except OSError:
        time.sleep(2)
else:
    raise SystemExit("Немає відповіді. Перевірте journalctl -u ec2-metadata.")
PYCHECK
