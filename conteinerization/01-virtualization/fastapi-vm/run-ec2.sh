#!/usr/bin/env bash
# Запуск навчального FastAPI всередині Ubuntu EC2.
set -Eeuo pipefail

if [[ "${1:-}" == "--help" ]]; then
  printf '%s\n' 'Запуск: bash run-ec2.sh' 'Параметри середовища: HOST=0.0.0.0 PORT=8000' 'Зупинка: Ctrl+C. Сервер працює, доки відкрита SSH-сесія.'
  exit 0
fi
if (( $# > 0 )); then
  printf '%s\n' 'Невідомий аргумент. Використайте --help.' >&2
  exit 2
fi
export HOST="${HOST:-0.0.0.0}" PORT="${PORT:-8000}"
if [[ ! "$PORT" =~ ^[0-9]{1,5}$ ]] || (( 10#$PORT < 1 || 10#$PORT > 65535 )); then
  printf '%s\n' 'PORT має бути цілим числом від 1 до 65535.' >&2
  exit 2
fi
PORT=$((10#$PORT))
export PORT
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"

if ! command -v python3 >/dev/null || ! python3 -c 'import venv, ensurepip' >/dev/null 2>&1; then
  if ! command -v apt-get >/dev/null; then
    printf '%s\n' 'Установіть Python 3.10+ з модулями venv та ensurepip.' >&2
    exit 1
  fi
  admin=()
  if (( EUID != 0 )); then
    command -v sudo >/dev/null || { printf '%s\n' 'Для встановлення python3-venv потрібен sudo.' >&2; exit 1; }
    admin=(sudo)
  fi
  "${admin[@]}" apt-get update
  "${admin[@]}" apt-get install -y python3 python3-venv
fi
python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else "Потрібен Python 3.10 або новіший.")'
if [[ ! -x .venv/bin/python ]]; then
  python3 -m venv .venv
fi
.venv/bin/python -m pip install --disable-pip-version-check -r requirements.txt
printf 'FastAPI: %s:%s; зупинка — Ctrl+C.\n' "$HOST" "$PORT"
exec .venv/bin/python -m uvicorn main:app --host "$HOST" --port "$PORT"
