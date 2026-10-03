#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
container_id=''
cleanup() {
  if [[ -n "$container_id" ]]; then docker rm -f "$container_id" >/dev/null; fi
}
trap cleanup EXIT
for form in direct simple-shell wait-shell explicit-shell; do
  docker build -q -f "Dockerfile.$form" -t "lecture3-nginx-$form:review" . >/dev/null
  container_id=$(docker run -d "lecture3-nginx-$form:review")
  ready=false
  for attempt in {1..30}; do
    if body=$(docker exec "$container_id" wget -qO- http://127.0.0.1:8080/ 2>/dev/null); then
      [[ "$body" == 'nginx is running' ]]
      ready=true
      break
    fi
    sleep 0.1
  done
  [[ "$ready" == true ]]
  docker exec "$container_id" htop --version >/dev/null
  # Діагностичні процеси вже завершилися перед знімком.
  snapshot=$(docker top "$container_id" -eo pid,ppid,args)
  root_pid=$(docker inspect --format '{{.State.Pid}}' "$container_id")
  printf '%s\n' "$snapshot" | awk -v root="$root_pid" -v form="$form" '
    NR>1 {
      n++; parent[$1]=$2
      if ($1==root) seen=1
      if ($0 ~ /nginx: master process/) master=$1
      if ($0 ~ /nginx: worker process/) worker=$1
    }
    END {
      shell=(form=="wait-shell" || form=="explicit-shell")
      if (!seen || !master || !worker || parent[worker]!=master) exit 1
      if (shell ? (n!=3 || parent[master]!=root) : (n!=2 || master!=root)) exit 1
    }'
  names=$(printf '%s\n' "$snapshot" | tail -n +2 | awk '
    /nginx: master process/ {print "nginx master";next}
    /nginx: worker process/ {print "nginx worker";next}
    {print "sh"}' | sort)
  count=$(printf '%s\n' "$names" | wc -l)
  printf '%s: %s\n%s\n\n' "$form" "$count" "$names"
  cleanup
  container_id=''
done
