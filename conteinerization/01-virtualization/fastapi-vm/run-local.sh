#!/usr/bin/env bash
# Локальний запуск навчального застосунку на власній машині, без VM.
set -Eeuo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
export HOST="${HOST:-127.0.0.1}" PORT="${PORT:-8000}"
python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else "Потрібен Python 3.10 або новіший.")'
if [[ ! -x .venv/bin/python ]]; then
  python3 -m venv .venv \
    || { printf '%s\n' 'Немає модуля venv: установіть пакет python3-venv.' >&2; exit 1; }
fi
if ! .venv/bin/python -c 'import fastapi, uvicorn' 2>/dev/null; then
  .venv/bin/python -m pip install --disable-pip-version-check -q -r requirements.txt
fi
printf 'Паспорт середовища: http://%s:%s ; зупинка — Ctrl+C.\n' "$HOST" "$PORT"
exec .venv/bin/python -m uvicorn main:app --host "$HOST" --port "$PORT"
