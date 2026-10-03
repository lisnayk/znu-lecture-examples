#!/usr/bin/env bash
set -euo pipefail
: "${REGION:?Задайте регіон репозиторію ECR}"
: "${REGISTRY:?Задайте URI реєстру ECR без шляху репозиторію}"
# Перед запуском створіть приватний репозиторій hello-image у ECR.
# AWS CLI має використовувати чинні credentials із дозволами ECR.
aws ecr get-login-password --region "$REGION" \
  | docker login --username AWS \
      --password-stdin "$REGISTRY"
docker tag hello-image:1.0 \
  "$REGISTRY/hello-image:1.0"
docker push "$REGISTRY/hello-image:1.0"
