#!/usr/bin/env bash
set -Eeuo pipefail
CONTAINER="${CONTAINER:-lecture3-multistage}"
IMAGE="${IMAGE:-multistage:1.0}"
docker rm -f "$CONTAINER"
docker rmi "$IMAGE" >/dev/null
