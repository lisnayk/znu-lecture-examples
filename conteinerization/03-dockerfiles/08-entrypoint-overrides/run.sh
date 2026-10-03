#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
docker build --quiet -t ep-demo:1.0 . >/dev/null
docker run --rm ep-demo:1.0
docker run --rm ep-demo:1.0 студенти
docker run --rm --entrypoint echo ep-demo:1.0 \
  "Інша програма"
