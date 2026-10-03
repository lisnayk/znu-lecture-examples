#!/usr/bin/env bash
# Розмір образу з двома етапами та без них.
set -Eeuo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
docker build -q -t multistage:1.0 . >/dev/null
docker build -q -f Dockerfile.single -t singlestage:1.0 . >/dev/null
for image in multistage:1.0 singlestage:1.0; do
  size=$(docker image inspect "$image" --format '{{.Size}}')
  printf '%-18s %s МБ\n' "$image" "$((size / 1000000))"
done
