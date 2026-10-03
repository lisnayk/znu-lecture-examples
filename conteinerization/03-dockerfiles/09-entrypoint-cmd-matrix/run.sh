#!/usr/bin/env bash
set -euo pipefail
# Перевірка конфігурації запуску, без виконання умовних app/tool.
for entry in none shell exec; do
  for cmd in none exec args shell; do
    case "$entry" in
      none) entry_line='ENTRYPOINT []' ;;
      shell) entry_line='ENTRYPOINT app -a' ;;
      exec) entry_line='ENTRYPOINT ["app", "-a"]' ;;
    esac
    case "$cmd" in
      none) cmd_line='CMD []' ;;
      exec) cmd_line='CMD ["tool", "-b"]' ;;
      args) cmd_line='CMD ["-p", "-q"]' ;;
      shell) cmd_line='CMD tool -b' ;;
    esac
    tag="lecture3-matrix-${entry}-${cmd}:review"
    printf 'FROM alpine:3.21\n%s\n%s\n' "$entry_line" "$cmd_line" | docker build -q -t "$tag" - >/dev/null
    if [[ "$entry" == none && "$cmd" == none ]]; then
      if result=$(docker create "$tag" 2>&1); then
        docker rm "$result" >/dev/null
        exit 1
      fi
      [[ "$result" == *'no command specified'* ]]
      printf '%s/%s: no command specified\n' "$entry" "$cmd"
      continue
    fi
    container_id=$(docker create "$tag")
    actual=$(docker inspect --format '{{json .Path}} {{json .Args}}' "$container_id")
    docker rm "$container_id" >/dev/null
    printf '%s/%s: %s\n' "$entry" "$cmd" "$actual"
  done
done
