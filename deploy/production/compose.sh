#!/usr/bin/env sh
set -eu

SCRIPT_DIR=$(CDPATH= cd "$(dirname "$0")" && pwd)
PROJECT_DIR=$(CDPATH= cd "$SCRIPT_DIR/../.." && pwd)
ENV_FILE="$PROJECT_DIR/.env"
COMPOSE_FILE="$SCRIPT_DIR/compose.yaml"

if [ ! -f "$ENV_FILE" ]; then
    echo "Arquivo .env não encontrado em $PROJECT_DIR." >&2
    echo "Use deploy/production/.env.example como referência e crie .env na raiz localmente." >&2
    exit 1
fi

exec docker compose \
    --project-name vozes-tcc \
    --project-directory "$PROJECT_DIR" \
    --file "$COMPOSE_FILE" \
    --env-file "$ENV_FILE" \
    "$@"
