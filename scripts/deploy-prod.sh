#!/usr/bin/env bash
# Atualiza o clone de produção e reconstrói o Compose (Caddy + web + Postgres).
# Na VM: bash scripts/deploy-prod.sh
# A Action passa DEPLOY_SHA=<40 hex> para publicar exatamente o commit do push.
set -euo pipefail

if [[ "$(id -u)" -eq 0 ]]; then
  if id ubuntu >/dev/null 2>&1; then
    exec sudo -u ubuntu -H env DEPLOY_SHA="${DEPLOY_SHA:-}" bash "$0" "$@"
  fi
  echo "rode como ubuntu (não como root)" >&2
  exit 1
fi

SCRIPT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_DIR="${DEPLOY_REPO_DIR:-$SCRIPT_ROOT}"
LOCK_FILE="${DEPLOY_LOCK_FILE:-/tmp/ib-conecta-deploy.lock}"
COMPOSE_FILE="docker-compose.prod.yml"
ENV_FILE=".env.prod"

cd "$REPO_DIR"

if [[ ! -f "$COMPOSE_FILE" ]]; then
  echo "não achei $COMPOSE_FILE em $REPO_DIR" >&2
  exit 1
fi
if [[ ! -f "$ENV_FILE" ]]; then
  echo "não achei $ENV_FILE em $REPO_DIR (não commite esse arquivo; copie de .env.prod.example)" >&2
  exit 1
fi

exec 9>"$LOCK_FILE"
if ! flock -n 9; then
  echo "já existe um deploy em andamento (lock $LOCK_FILE)" >&2
  exit 1
fi

if [[ -n "${DEPLOY_SHA:-}" && ! "${DEPLOY_SHA}" =~ ^[0-9a-f]{40}$ ]]; then
  echo "DEPLOY_SHA inválido (esperado 40 hex): ${DEPLOY_SHA}" >&2
  exit 1
fi

echo "deploy em $REPO_DIR (user=$(id -un) sha=${DEPLOY_SHA:-origin/master})"

git fetch --prune origin master
if [[ -n "${DEPLOY_SHA:-}" ]]; then
  git rev-parse --verify "${DEPLOY_SHA}^{commit}" >/dev/null
  git checkout -B master "$DEPLOY_SHA"
else
  git checkout -B master origin/master
fi

echo "HEAD $(git rev-parse HEAD) $(git log -1 --oneline)"

compose() {
  docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" "$@"
}

compose up --build -d --wait --wait-timeout 300
compose ps
echo "OK deploy $(git rev-parse --short HEAD)"
