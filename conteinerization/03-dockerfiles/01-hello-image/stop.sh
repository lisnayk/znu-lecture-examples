#!/usr/bin/env bash
# Зупинка контейнера й видалення зібраного образу.
set -Eeuo pipefail
CONTAINER="${CONTAINER:-lecture3-hello}"
IMAGE="${IMAGE:-hello-image:1.0}"
docker rm -f "$CONTAINER"
docker rmi "$IMAGE"
