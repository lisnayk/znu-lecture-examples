#!/usr/bin/env bash
# Користувацькі дані (user data) для інстанса EC2 з Ubuntu Server.
# cloud-init виконує цей скрипт від root під час першого запуску інстанса,
# тому підключатися по SSH для старту застосунку не потрібно.
# Журнал виконання: /var/log/cloud-init-output.log
set -Eeuo pipefail

REPO="https://github.com/lisnayk/znu-lecture-examples.git"
DIR="/opt/passport"
APP="$DIR/conteinerization/01-virtualization/fastapi-vm"
PORT="${PORT:-8000}"

export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y git python3 python3-venv

rm -rf "$DIR"
git clone --depth 1 "$REPO" "$DIR"

python3 -m venv "$APP/.venv"
"$APP/.venv/bin/python" -m pip install --disable-pip-version-check -q -r "$APP/requirements.txt"

# Окремий службовий користувач: застосунок не потребує прав root.
id -u passport >/dev/null 2>&1 || useradd --system --home-dir "$APP" --shell /usr/sbin/nologin passport
chown -R passport:passport "$DIR"

cat > /etc/systemd/system/passport.service <<UNIT
[Unit]
Description=Passport of environment (educational FastAPI application)
After=network-online.target
Wants=network-online.target

[Service]
User=passport
WorkingDirectory=$APP
ExecStart=$APP/.venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port $PORT
Restart=on-failure

[Install]
WantedBy=multi-user.target
UNIT

systemctl daemon-reload
systemctl enable --now passport.service

# Самоперевірка: п'ять рядків PASS мають з'явитися у журналі cloud-init.
for _ in $(seq 1 30); do
  curl -sf -o /dev/null "http://127.0.0.1:$PORT/healthz" && break
  sleep 2
done
"$APP/.venv/bin/python" "$APP/check.py" "http://127.0.0.1:$PORT" || echo 'Перевірка не пройшла: див. systemctl status passport'
