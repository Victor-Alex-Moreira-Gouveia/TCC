#!/bin/sh
set -eu

gunicorn --bind 127.0.0.1:8081 --workers 1 wsgi:app >/tmp/vozes-tcc-test-server.log 2>&1 &
server_pid=$!

cleanup() {
    kill "$server_pid" 2>/dev/null || true
    wait "$server_pid" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

python - <<'PY'
import time
import urllib.error
import urllib.request

for attempt in range(30):
    try:
        with urllib.request.urlopen('http://127.0.0.1:8081/health', timeout=2) as response:
            if response.status == 200:
                break
    except (OSError, urllib.error.URLError):
        time.sleep(1)
else:
    raise SystemExit('Servidor de teste não ficou pronto; consulte /tmp/vozes-tcc-test-server.log.')
PY

pytest -q test_crud.py
