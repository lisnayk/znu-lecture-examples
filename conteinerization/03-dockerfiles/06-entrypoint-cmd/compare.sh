#!/usr/bin/env bash
# Три спостережувані відмінності форм запису ENTRYPOINT і CMD.
set -Eeuo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"

for name in shell exec loop simple both; do
  docker build -q -f "Dockerfile.$name" -t "ep-$name:1.0" . >/dev/null
done

echo '1. Підстановка змінної середовища'
printf '   shell: '; docker run --rm ep-shell:1.0
printf '   exec:  '; docker run --rm ep-exec:1.0

echo
echo '2. Головний процес контейнера'
for image in ep-simple:1.0 ep-loop:1.0; do
  docker rm -f ep-demo >/dev/null 2>&1 || true
  docker run -d --name ep-demo "$image" >/dev/null
  sleep 1
  printf '   %-14s PID 1: %s\n' "$image" "$(docker exec ep-demo ps -o pid,args | awk '$1==1{$1="";print substr($0,2)}')"
  docker rm -f ep-demo >/dev/null
done

echo
echo '3. CMD задає аргументи за замовчуванням для ENTRYPOINT'
printf '   без аргументів:        '; docker run --rm ep-both:1.0 | sed -n '1p'
printf '   з аргументом ::1:      '; docker run --rm ep-both:1.0 ::1 | sed -n '1p'
