#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
container_id=''
cleanup() {
  if [[ -n "$container_id" ]]; then docker rm -f "$container_id" >/dev/null; fi
}
trap cleanup EXIT
for form in direct simple-shell wait-shell explicit-shell; do
  docker build -q -f "Dockerfile.$form" -t "lecture3-process-$form:review" . >/dev/null
  container_id=$(docker run -d "lecture3-process-$form:review")
  sleep 0.3
  snapshot=$(docker top "$container_id" -eo pid,ppid,comm)
  names=$(printf '%s\n' "$snapshot" | tail -n +2 | awk '{print $3}' | sort)
  root_pid=$(docker inspect --format '{{.State.Pid}}' "$container_id")
  printf '%s\n' "$snapshot" | awk -v root="$root_pid" 'NR>1 {if ($1==root) seen=1; else if ($2!=root) bad=1} END {exit !seen || bad}'
  count=$(printf '%s\n' "$names" | wc -l)
  printf '%s: %s\n%s\n\n' "$form" "$count" "$names"
  cleanup
  container_id=''
done
