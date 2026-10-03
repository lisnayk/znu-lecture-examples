#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
docker build -t lecture3-signals-review . >/dev/null
cid=''
trap 'if [ -n "$cid" ]; then docker rm -f "$cid" >/dev/null; fi' EXIT
ready() {
  for attempt in $(seq 1 50); do
    if docker logs "$cid" 2>&1 | grep -q READY; then return; fi
    sleep 0.1
  done
  return 1
}
cid=$(docker run -d lecture3-signals-review)
ready
docker stop --timeout 3 "$cid" >/dev/null
docker logs "$cid" | grep -q 'SIGTERM: завершення роботи'
printf 'SIGTERM exit=%s\n' "$(docker inspect "$cid" --format '{{.State.ExitCode}}')"
docker rm "$cid" >/dev/null
cid=$(docker run -d lecture3-signals-review)
ready
docker kill --signal SIGINT "$cid" >/dev/null
docker wait "$cid" >/dev/null
docker logs "$cid" | grep -q 'SIGINT: завершення роботи'
printf 'SIGINT exit=%s\n' "$(docker inspect "$cid" --format '{{.State.ExitCode}}')"
docker rm "$cid" >/dev/null
cid=$(docker run -d -e IGNORE_TERM=1 lecture3-signals-review)
ready
docker stop --timeout 1 "$cid" >/dev/null
printf 'SIGKILL exit=%s\n' "$(docker inspect "$cid" --format '{{.State.ExitCode}}')"
docker rm "$cid" >/dev/null
cid=''
