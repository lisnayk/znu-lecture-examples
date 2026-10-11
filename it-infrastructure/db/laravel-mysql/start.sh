#!/bin/bash
set -Eeuo pipefail
cd "$(dirname "$0")"
php artisan migrate --force --no-interaction
if [[ "${1:-}" == --migrate-only ]]; then
  exit 0
fi
exec php artisan serve --host="${APP_BIND_HOST:-127.0.0.1}" --port="${APP_BIND_PORT:-8767}" --no-reload
