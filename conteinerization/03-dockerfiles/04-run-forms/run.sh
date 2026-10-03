#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
docker build -t lecture3-run-review .
docker run --rm lecture3-run-review
