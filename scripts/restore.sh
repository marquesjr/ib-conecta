#!/usr/bin/env bash
# Decrypt a backup artifact and restore PostgreSQL (throwaway by default).
# Restoring into the live Compose database requires --into compose --yes.
set -euo pipefail
umask 077

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

SOURCE=""
IDENTITY=""
INTO="throwaway"
ASSUME_YES=0
KEEP=0

usage() {
  cat <<'EOF'
Usage: scripts/restore.sh --from <s3://bucket/key | file.age> --identity <age-key> [options]

Options:
  --into throwaway   Restore into a disposable postgres:16 container (default)
  --into compose     Restore into the running Compose db (DESTROYS current data)
  --yes              Required for --into compose
  --keep             Do not remove the throwaway container
  --help

Environment: same BACKUP_* / AWS_* as scripts/backup.sh, plus BACKUP_AGE_IDENTITY.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --from)
      SOURCE="${2:?}"
      shift 2
      ;;
    --identity)
      IDENTITY="${2:?}"
      shift 2
      ;;
    --into)
      INTO="${2:?}"
      shift 2
      ;;
    --yes)
      ASSUME_YES=1
      shift
      ;;
    --keep)
      KEEP=1
      shift
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

if [[ -f "$ROOT/.env.backup" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "$ROOT/.env.backup"
  set +a
fi

IDENTITY="${IDENTITY:-${BACKUP_AGE_IDENTITY:-}}"
SOURCE="${SOURCE:-${BACKUP_RESTORE_FROM:-}}"
BACKUP_S3_REGION="${BACKUP_S3_REGION:-us-east-2}"
BACKUP_COMPOSE_FILE="${BACKUP_COMPOSE_FILE:-docker-compose.prod.yml}"
if [[ -z "${BACKUP_ENV_FILE:-}" ]]; then
  if [[ "$BACKUP_COMPOSE_FILE" == *prod* ]]; then
    BACKUP_ENV_FILE=".env.prod"
  else
    BACKUP_ENV_FILE=".env"
  fi
fi
if [[ "$BACKUP_COMPOSE_FILE" != /* && "$BACKUP_COMPOSE_FILE" != [A-Za-z]:* ]]; then
  BACKUP_COMPOSE_FILE="$ROOT/$BACKUP_COMPOSE_FILE"
fi
if [[ "$BACKUP_ENV_FILE" != /* && "$BACKUP_ENV_FILE" != [A-Za-z]:* ]]; then
  BACKUP_ENV_FILE="$ROOT/$BACKUP_ENV_FILE"
fi

if [[ -z "$SOURCE" || -z "$IDENTITY" ]]; then
  usage >&2
  exit 1
fi
if [[ "$IDENTITY" != /* && "$IDENTITY" != [A-Za-z]:* ]]; then
  IDENTITY="$ROOT/$IDENTITY"
fi
if [[ ! -f "$IDENTITY" ]]; then
  echo "Missing age identity: $IDENTITY" >&2
  exit 1
fi
if [[ "$INTO" == "compose" && "$ASSUME_YES" -ne 1 ]]; then
  echo "--into compose requires --yes (this replaces the live database)." >&2
  exit 1
fi

python_bin() {
  if command -v python3 >/dev/null 2>&1; then
    command python3 "$@"
  else
    command python "$@"
  fi
}

find_bin() {
  local name="$1"
  shift
  if command -v "$name" >/dev/null 2>&1; then
    command -v "$name"
    return 0
  fi
  local candidate
  for candidate in "$@"; do
    if [[ -x "$candidate" ]]; then
      printf '%s' "$candidate"
      return 0
    fi
  done
  echo "Missing command: $name" >&2
  return 1
}

AGE_BIN="$(find_bin age \
  "$ROOT/.scratch/age-bin/age/age.exe" \
  "$ROOT/.scratch/age-bin/age/age" \
  /usr/bin/age)"
AWS_BIN="$(find_bin aws \
  "/c/Program Files/Amazon/AWSCLIV2/aws.exe" \
  "/mnt/c/Program Files/Amazon/AWSCLIV2/aws.exe" \
  /usr/bin/aws \
  /usr/local/bin/aws)"

aws_cli() {
  local extra=()
  if [[ -n "${AWS_ENDPOINT_URL:-}" ]]; then
    extra+=(--endpoint-url "$AWS_ENDPOINT_URL")
  fi
  "$AWS_BIN" --region "$BACKUP_S3_REGION" "${extra[@]}" "$@"
}

compose() {
  local args=(docker compose -f "$BACKUP_COMPOSE_FILE")
  if [[ -f "$BACKUP_ENV_FILE" ]]; then
    args+=(--env-file "$BACKUP_ENV_FILE")
  fi
  "${args[@]}" "$@"
}

WORK="$(mktemp -d "${TMPDIR:-/tmp}/ib-conecta-restore.XXXXXX")"
cleanup() {
  rm -rf "$WORK"
}
trap cleanup EXIT

ARTIFACT="$WORK/backup.tar.age"
if [[ "$SOURCE" == s3://* ]]; then
  echo "Downloading $SOURCE"
  aws_cli s3 cp "$SOURCE" "$ARTIFACT"
else
  if [[ "$SOURCE" != /* && "$SOURCE" != [A-Za-z]:* ]]; then
    SOURCE="$ROOT/$SOURCE"
  fi
  cp "$SOURCE" "$ARTIFACT"
fi

echo "Decrypting..."
"$AGE_BIN" -d -i "$IDENTITY" -o "$WORK/backup.tar" "$ARTIFACT"
tar -C "$WORK" -xf "$WORK/backup.tar"
test -s "$WORK/db.dump"
test -s "$WORK/MANIFEST"
echo "MANIFEST:"
cat "$WORK/MANIFEST"
echo "media.tgz contents (first 20):"
tar tzf "$WORK/media.tgz" | head -n 20 || true

docker_cp_in() {
  # Git Bash otherwise rewrites /tmp inside the container to a Windows path.
  local src="$1" dest="$2"
  if command -v cygpath >/dev/null 2>&1; then
    src="$(cygpath -w "$src")"
  fi
  MSYS_NO_PATHCONV=1 docker cp "$src" "$dest"
}

verify_sql() {
  local cid="$1"
  local user="$2"
  local db="$3"
  docker exec -e PGPASSWORD="${4:-}" "$cid" \
    psql -U "$user" -d "$db" -Atc "SELECT COUNT(*) FROM django_migrations;"
}

if [[ "$INTO" == "throwaway" ]]; then
  NAME="ib-conecta-restore-test"
  docker rm -f "$NAME" >/dev/null 2>&1 || true
  echo "Starting throwaway postgres:16-alpine ($NAME)..."
  docker run -d --name "$NAME" \
    -e POSTGRES_USER=ibconecta \
    -e POSTGRES_PASSWORD=restore-test \
    -e POSTGRES_DB=ibconecta \
    postgres:16-alpine >/dev/null
  if [[ "$KEEP" -ne 1 ]]; then
    trap 'docker rm -f ib-conecta-restore-test >/dev/null 2>&1 || true; rm -rf "$WORK"' EXIT
  fi
  for _ in $(seq 1 30); do
    if docker exec "$NAME" pg_isready -U ibconecta -d ibconecta >/dev/null 2>&1; then
      break
    fi
    sleep 1
  done
  docker_cp_in "$WORK/db.dump" "$NAME:/tmp/db.dump"
  echo "Restoring dump..."
  set +e
  MSYS_NO_PATHCONV=1 docker exec "$NAME" pg_restore -U ibconecta -d ibconecta --no-owner --no-acl /tmp/db.dump
  restore_rc=$?
  set -e
  if [[ "$restore_rc" -gt 1 ]]; then
    echo "pg_restore failed with status $restore_rc" >&2
    exit "$restore_rc"
  fi
  COUNT="$(verify_sql "$NAME" ibconecta ibconecta restore-test | tr -d '\r')"
  echo "django_migrations=${COUNT}"
  if [[ "$COUNT" -lt 1 ]]; then
    echo "Restore produced an empty migration table." >&2
    exit 1
  fi
  echo "OK throwaway restore ($NAME)"
  if [[ "$KEEP" -eq 1 ]]; then
    echo "Container kept. Password: restore-test. Remove with: docker rm -f $NAME"
  fi
  exit 0
fi

echo "Restoring into Compose database (destructive)..."
POSTGRES_USER="$(compose exec -T db printenv POSTGRES_USER | tr -d '\r')"
POSTGRES_DB="$(compose exec -T db printenv POSTGRES_DB | tr -d '\r')"
compose cp "$WORK/db.dump" db:/tmp/db.dump
set +e
MSYS_NO_PATHCONV=1 compose exec -T db pg_restore -U "$POSTGRES_USER" -d "$POSTGRES_DB" --no-owner --no-acl --clean --if-exists /tmp/db.dump
restore_rc=$?
set -e
if [[ "$restore_rc" -gt 1 ]]; then
  echo "pg_restore failed with status $restore_rc" >&2
  exit "$restore_rc"
fi
compose exec -T db rm -f /tmp/db.dump
COUNT="$(compose exec -T db psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Atc "SELECT COUNT(*) FROM django_migrations;" | tr -d '\r')"
echo "django_migrations=${COUNT}"

PROJECT="$(compose config --format json 2>/dev/null | python_bin -c 'import json,sys; print(json.load(sys.stdin)["name"])' || true)"
if [[ -n "${PROJECT:-}" ]]; then
  MEDIA_VOL="${PROJECT}_media_data"
  PRIVATE_VOL="${PROJECT}_private_media_data"
  if docker volume inspect "$MEDIA_VOL" >/dev/null 2>&1 || docker volume inspect "$PRIVATE_VOL" >/dev/null 2>&1; then
    RUN_VOLS=()
    docker volume inspect "$MEDIA_VOL" >/dev/null 2>&1 && RUN_VOLS+=(-v "$MEDIA_VOL:/restore/media")
    docker volume inspect "$PRIVATE_VOL" >/dev/null 2>&1 && RUN_VOLS+=(-v "$PRIVATE_VOL:/restore/private_media")
    docker run --rm "${RUN_VOLS[@]}" -v "$WORK:/in:ro" alpine:3.20 \
      sh -c 'rm -rf /restore/media/* /restore/private_media/*; tar xzf /in/media.tgz -C /restore'
  fi
fi
echo "OK compose restore"
