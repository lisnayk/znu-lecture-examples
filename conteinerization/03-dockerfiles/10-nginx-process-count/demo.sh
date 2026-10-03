#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
if [[ ! -t 0 || ! -t 1 ]]; then
  printf 'Запустіть demo.sh в інтерактивному терміналі.\n' >&2
  exit 1
fi
container_id=''
cleanup() {
  if [[ -n "$container_id" ]]; then docker rm -f "$container_id" >/dev/null; fi
}
trap cleanup EXIT
trap 'exit 130' INT
for form in direct simple-shell wait-shell explicit-shell; do
  docker build -q -f "Dockerfile.$form" -t "lecture3-nginx-$form:review" . >/dev/null
done
for form in direct simple-shell wait-shell explicit-shell; do
  clear
  printf '\nВаріант %s\n\n' "$form"
  sed -n '1,4p' "Dockerfile.$form"
  printf '\nКонфігурація: daemon off; worker_processes 1;\n'
  container_id=$(docker run -d "lecture3-nginx-$form:review")
  ready=false
  for attempt in {1..30}; do
    if docker exec "$container_id" wget -qO- http://127.0.0.1:8080/ >/dev/null 2>&1; then ready=true; break; fi
    sleep 0.1
  done
  [[ "$ready" == true ]]
  snapshot=$(docker top "$container_id" -eo pid,ppid,args)
  count=$(printf '%s\n' "$snapshot" | tail -n +2 | wc -l)
  printf '\nДо запуску htop: %s процеси.\n' "$count"
  printf '%s\n' "$snapshot"
  printf '\nУ htop буде ще один процес — сам htop.\n'
  printf 'PID 1 — nginx master або sh; нижче видно nginx worker.\n'
  printf 'F5 перемикає дерево, q виходить із htop.\n'
  read -r -p 'Натисніть Enter, щоб відкрити htop... ' reply
  docker exec -it -e TERM=xterm "$container_id" htop --tree
  cleanup
  container_id=''
  read -r -p 'Натисніть Enter для наступного варіанта... ' reply
done
printf '\nУсі чотири варіанти переглянуто. Контейнери демонстрації видалено.\n'
