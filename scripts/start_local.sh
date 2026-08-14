#!/usr/bin/env bash
set -euo pipefail

# Usage: ./scripts/start_local.sh
# Creates (if needed) a virtualenv at .venv, installs requirements and starts the app.
# If gunicorn is available it will be used; otherwise Flask's development server is used.

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
PYTHON=${PYTHON:-python3}
VENV_DIR=${VENV_DIR:-.venv}

if [ ! -d "$VENV_DIR" ]; then
  echo "Creating virtualenv at $VENV_DIR..."
  $PYTHON -m venv "$VENV_DIR"
fi

# Activate
# shellcheck source=/dev/null
. "$VENV_DIR/bin/activate"

pip install --upgrade pip
pip install -r Server/requirements.txt

# Load .env into environment (if present)
if [ -f .env ]; then
  echo "Loading .env variables into environment"
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

# Prefer gunicorn if available in the venv
if command -v gunicorn >/dev/null 2>&1; then
  echo "Starting with gunicorn"
  cd Server
  gunicorn --bind 0.0.0.0:8080 wsgi:app
else
  echo "Starting with Flask development server (FLASK_ENV not set to production)"
  export FLASK_APP=Server.main
  python -m flask run --host=0.0.0.0 --port=8080
fi
