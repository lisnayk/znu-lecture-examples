#!/usr/bin/env bash
# Збірка багатоетапного образу та запуск контейнера з нього.
set -Eeuo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
IMAGE="${IMAGE:-multistage:1.0}"
CONTAINER="${CONTAINER:-lecture3-multistage}"
PORT="${PORT:-8080}"

docker build -t "$IMAGE" .
docker rm -f "$CONTAINER" >/dev/null 2>&1 || true
docker run -d --name "$CONTAINER" -p "$PORT:80" "$IMAGE"

printf 'Сторінка: http://127.0.0.1:%s ; зупинка — bash stop.sh\n' "$PORT"
