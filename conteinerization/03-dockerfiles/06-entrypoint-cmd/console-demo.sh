#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
for form in shell exec; do
  docker build -q -f "Dockerfile.$form" -t "ep-$form:1.0" . >/dev/null
done
printf '$ docker run --rm ep-shell:1.0\n'
docker run --rm ep-shell:1.0
printf '\n$ docker run --rm ep-exec:1.0\n'
docker run --rm ep-exec:1.0
