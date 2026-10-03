#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
for form in direct simple-shell wait-shell explicit-shell; do
  docker build -q -f "Dockerfile.$form" -t "lecture3-nginx-$form:review" . >/dev/null
done
container_id=''
cleanup() {
  if [[ -n "$container_id" ]]; then docker rm -f "$container_id" >/dev/null; fi
}
trap cleanup EXIT
printf 'form\trun\telapsed_ms\texit_code\toom\tkill_signals\n'
for run in 1 2 3; do
  for form in direct simple-shell wait-shell explicit-shell; do
    container_id=$(docker run -d --stop-signal SIGTERM "lecture3-nginx-$form:review")
    ready=false
    for attempt in {1..30}; do
      if docker exec "$container_id" wget -qO- http://127.0.0.1:8080/ >/dev/null 2>&1; then ready=true; break; fi
      sleep 0.1
    done
    [[ "$ready" == true ]]
    since=$(date +%s)
    elapsed=$(node --input-type=module -e '
      import {execFileSync} from "node:child_process";
      const start=process.hrtime.bigint();
      execFileSync("docker",["stop","--timeout","5",process.argv[1]],{stdio:"ignore"});
      console.log(Number(process.hrtime.bigint()-start)/1e6);
    ' "$container_id")
    exit_code=$(docker inspect --format '{{.State.ExitCode}}' "$container_id")
    oom=$(docker inspect --format '{{.State.OOMKilled}}' "$container_id")
    until=$(date +%s)
    signals=$(docker events --since "$since" --until "$((until+1))" --filter "container=$container_id" --filter event=kill --format '{{index .Actor.Attributes "signal"}}' | paste -sd , -)
    printf '%s\t%s\t%.0f\t%s\t%s\t%s\n' "$form" "$run" "$elapsed" "$exit_code" "$oom" "$signals"
    cleanup
    container_id=''
  done
done
