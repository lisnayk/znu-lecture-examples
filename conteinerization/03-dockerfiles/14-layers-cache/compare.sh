#!/usr/bin/env bash
# Дві різні речі, які часто плутають: кількість шарів і розмір образу.
set -Eeuo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"

build(){ docker build -q -f "$1" -t "$2" . >/dev/null; }
show(){
  local image=$1
  local layers size
  layers=$(docker image inspect "$image" --format '{{len .RootFS.Layers}}')
  size=$(docker image inspect "$image" --format '{{.Size}}')
  printf '%-18s шарів: %s, розмір: %s МБ\n' "$image" "$layers" "$((size / 1000000))"
}

echo 'Кількість шарів: чотири RUN проти одного'
build Dockerfile.many layers-many:1.0;  show layers-many:1.0
build Dockerfile.one  layers-one:1.0;   show layers-one:1.0

echo
echo 'Розмір образу: видалення файла в наступному шарі його не зменшує'
build Dockerfile.leak  layers-leak:1.0;  show layers-leak:1.0
build Dockerfile.clean layers-clean:1.0; show layers-clean:1.0
