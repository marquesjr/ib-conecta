#!/usr/bin/env bash
# Discard retreat medical/minor data past the event retention window.
# See docs/privacidade.md.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ -z "${BACKUP_COMPOSE_FILE:-}" ]]; then
  if [[ -f "$ROOT/docker-compose.prod.yml" && -f "$ROOT/.env.prod" ]]; then
    BACKUP_COMPOSE_FILE="$ROOT/docker-compose.prod.yml"
    BACKUP_ENV_FILE="${BACKUP_ENV_FILE:-$ROOT/.env.prod}"
  else
    BACKUP_COMPOSE_FILE="$ROOT/docker-compose.yml"
    BACKUP_ENV_FILE="${BACKUP_ENV_FILE:-$ROOT/.env}"
  fi
fi
if [[ "$BACKUP_COMPOSE_FILE" != /* && "$BACKUP_COMPOSE_FILE" != [A-Za-z]:* ]]; then
  BACKUP_COMPOSE_FILE="$ROOT/$BACKUP_COMPOSE_FILE"
fi
if [[ -z "${BACKUP_ENV_FILE:-}" ]]; then
  BACKUP_ENV_FILE="$ROOT/.env.prod"
fi
if [[ "$BACKUP_ENV_FILE" != /* && "$BACKUP_ENV_FILE" != [A-Za-z]:* ]]; then
  BACKUP_ENV_FILE="$ROOT/$BACKUP_ENV_FILE"
fi

args=(docker compose -f "$BACKUP_COMPOSE_FILE")
if [[ -f "$BACKUP_ENV_FILE" ]]; then
  args+=(--env-file "$BACKUP_ENV_FILE")
fi
"${args[@]}" exec -T web python manage.py discard_retreat_sensitive_data
