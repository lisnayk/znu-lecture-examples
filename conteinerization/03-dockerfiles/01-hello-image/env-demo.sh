#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
docker build -f Dockerfile.overview -t lecture3-env .
docker run --rm lecture3-env printenv PORT
docker run --rm -e PORT=8080 lecture3-env printenv PORT
docker image inspect lecture3-env --format '{{json .Config.Env}}'
