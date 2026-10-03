#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
docker build --build-arg APP_VERSION=2.0 -t lecture3-arg-review .
docker image inspect lecture3-arg-review --format '{{index .Config.Labels "org.opencontainers.image.version"}}'
docker run --rm lecture3-arg-review
