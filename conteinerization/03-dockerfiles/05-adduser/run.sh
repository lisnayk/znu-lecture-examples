#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
docker build -t lecture3-adduser-review .
docker run --rm lecture3-adduser-review
docker run --rm lecture3-adduser-review id -un
