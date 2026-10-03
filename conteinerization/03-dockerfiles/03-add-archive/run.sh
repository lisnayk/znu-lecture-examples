#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
tar -cf site.tar -C site index.html
docker build -t lecture3-add-review .
docker run --rm lecture3-add-review
docker run --rm lecture3-add-review sh -c 'test -f /copied/site.tar && test ! -e /copied/index.html && test ! -e /app/site.tar && echo "COPY зберіг архів без розпакування"'
