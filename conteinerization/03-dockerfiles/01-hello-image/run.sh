#!/usr/bin/env bash
# Збірка власного образу та запуск контейнера з нього.
set -Eeuo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
IMAGE="${IMAGE:-hello-image:1.0}"
CONTAINER="${CONTAINER:-lecture3-hello}"
PORT="${PORT:-3000}"

docker build -t "$IMAGE" .
docker rm -f "$CONTAINER" >/dev/null 2>&1 || true
docker run -d --name "$CONTAINER" -p "$PORT:3000" "$IMAGE"

printf 'Сторінка: http://127.0.0.1:%s ; зупинка — bash stop.sh\n' "$PORT"
