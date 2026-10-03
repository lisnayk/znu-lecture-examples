#!/usr/bin/env bash
set -euo pipefail
: "${HUB_USER:?Задайте HUB_USER, свій Docker ID}"
# Перед запуском створіть репозиторій hello-image у Docker Hub.
# Уведіть персональний access token у запиті пароля.
docker login --username "$HUB_USER"
docker tag hello-image:1.0 \
  "$HUB_USER/hello-image:1.0"
docker push "$HUB_USER/hello-image:1.0"
