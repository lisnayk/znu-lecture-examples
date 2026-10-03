#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
bash -n hub.sh ecr.sh
docker() {
  if [[ " $* " == *' --password-stdin '* ]]; then
    local dummy
    IFS= read -r dummy
    [[ "$dummy" == 'test-token-not-a-credential' ]]
  fi
  printf 'docker'
  printf ' <%s>' "$@"
  printf '\n'
}
aws() {
  [[ "$*" == 'ecr get-login-password --region us-east-1' ]]
  printf '%s\n' 'test-token-not-a-credential'
}
export -f docker aws
export HUB_USER=student-example REGION=us-east-1
export REGISTRY=123456789012.dkr.ecr.us-east-1.amazonaws.com
actual=$( { bash hub.sh; bash ecr.sh; } )
diff -u expected.txt <(printf '%s\n' "$actual")
printf 'PASS аргументи команд і передавання тестового токена через stdin\n'
