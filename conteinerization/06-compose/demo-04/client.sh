#!/usr/bin/env bash
set -euo pipefail

database=$(mysql -h db -u demo -Nse 'SELECT DATABASE()' shop)
printf 'MySQL: %s\n' "$database"

exec 3<>/dev/tcp/cache/11211
case "${1:?Вкажіть seed або read}" in
  seed)
    printf 'set database 0 0 %s\r\n%s\r\n' "${#database}" "$database" >&3
    IFS= read -r -t 3 reply <&3
    test "$reply" = $'STORED\r'
    printf 'Memcached: STORED\n'
    ;;
  read)
    printf 'get database\r\n' >&3
    IFS= read -r -t 3 header <&3
    IFS= read -r -t 3 cached <&3
    IFS= read -r -t 3 end <&3
    [[ "$header" == VALUE\ database\ * && "$end" == $'END\r' ]]
    test "${cached%$'\r'}" = "$database"
    printf 'Memcached: %s\n' "${cached%$'\r'}"
    ;;
  *)
    exit 2
    ;;
esac
