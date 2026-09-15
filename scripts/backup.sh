#!/usr/bin/env bash
# Daily encrypted backup: pg_dump + media + config.env → age → S3.
# See docs/backup.md. Identity never lives on the VM; only the recipient.
set -euo pipefail
umask 077

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
  cat <<'EOF'
Usage: scripts/backup.sh

Reads BACKUP_* and optional AWS_* from the environment and/or .env.backup.

Required:
  BACKUP_S3_BUCKET          Destination bucket
  BACKUP_AGE_RECIPIENTS     File with age1... recipients (default: backup/age-recipients.txt)

Optional:
  BACKUP_COMPOSE_FILE       default docker-compose.prod.yml
  BACKUP_ENV_FILE           default .env.prod (or .env if compose file is not prod)
  BACKUP_S3_REGION          default us-east-2
  AWS_ENDPOINT_URL          LocalStack, e.g. http://localhost:4566
  BACKUP_WORKDIR            scratch directory (deleted on exit)
  BACKUP_SKIP_DISCARD=1     skip discard_retreat_sensitive_data before the dump
EOF
  exit 0
fi

if [[ -f "$ROOT/.env.backup" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "$ROOT/.env.backup"
  set +a
fi

BACKUP_S3_BUCKET="${BACKUP_S3_BUCKET:?Set BACKUP_S3_BUCKET (or put it in .env.backup)}"
BACKUP_S3_REGION="${BACKUP_S3_REGION:-us-east-2}"
BACKUP_AGE_RECIPIENTS="${BACKUP_AGE_RECIPIENTS:-$ROOT/backup/age-recipients.txt}"
if [[ "$BACKUP_AGE_RECIPIENTS" != /* && "$BACKUP_AGE_RECIPIENTS" != [A-Za-z]:* ]]; then
  BACKUP_AGE_RECIPIENTS="$ROOT/$BACKUP_AGE_RECIPIENTS"
fi
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

if [[ ! -f "$BACKUP_AGE_RECIPIENTS" ]]; then
  echo "Missing age recipients file: $BACKUP_AGE_RECIPIENTS" >&2
  exit 1
fi
if [[ ! -f "$BACKUP_COMPOSE_FILE" ]]; then
  echo "Missing compose file: $BACKUP_COMPOSE_FILE" >&2
  exit 1
fi
if [[ ! -f "$BACKUP_ENV_FILE" ]]; then
  echo "Missing env file: $BACKUP_ENV_FILE" >&2
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

compose_project() {
  local json
  if json="$(compose config --format json 2>/dev/null)"; then
    printf '%s' "$json" | python_bin -c 'import json,sys; print(json.load(sys.stdin)["name"])'
    return
  fi
  python_bin -c 'import pathlib,re,sys
text=pathlib.Path(sys.argv[1]).read_text(encoding="utf-8")
m=re.search(r"^name:\s*(\S+)", text, re.M)
print(m.group(1) if m else pathlib.Path(".").resolve().name)
' "$BACKUP_COMPOSE_FILE"
}

if command -v flock >/dev/null 2>&1 && [[ -z "${BACKUP_LOCK_HELD:-}" ]]; then
  export BACKUP_LOCK_HELD=1
  exec flock -n /tmp/ib-conecta-backup.lock "$0" "$@"
fi

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
DAY="$(date -u +%Y-%m-%d)"
MONTH="$(date -u +%Y-%m)"
FILENAME="ib-conecta-${STAMP}.tar.age"
DAILY_KEY="daily/${DAY}/${FILENAME}"
MONTHLY_KEY="monthly/${MONTH}/${FILENAME}"

WORK="${BACKUP_WORKDIR:-$(mktemp -d "${TMPDIR:-/tmp}/ib-conecta-backup.XXXXXX")}"
mkdir -p "$WORK"
cleanup() {
  rm -rf "$WORK"
}
trap cleanup EXIT

echo "Backing up into $WORK"

if [[ "${BACKUP_SKIP_DISCARD:-}" != "1" ]]; then
  echo "Discarding due retreat sensitive data..."
  compose exec -T web python manage.py discard_retreat_sensitive_data
fi

echo "Dumping PostgreSQL..."
POSTGRES_USER="$(compose exec -T db printenv POSTGRES_USER | tr -d '\r')"
POSTGRES_DB="$(compose exec -T db printenv POSTGRES_DB | tr -d '\r')"
compose exec -T db pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc >"$WORK/db.dump"
test -s "$WORK/db.dump"

echo "Archiving media..."
PROJECT="$(compose_project)"
MEDIA_VOL="${PROJECT}_media_data"
PRIVATE_VOL="${PROJECT}_private_media_data"
HAVE_VOL=0
RUN_VOLS=()
if docker volume inspect "$MEDIA_VOL" >/dev/null 2>&1; then
  RUN_VOLS+=(-v "$MEDIA_VOL:/backup/media:ro")
  HAVE_VOL=1
fi
if docker volume inspect "$PRIVATE_VOL" >/dev/null 2>&1; then
  RUN_VOLS+=(-v "$PRIVATE_VOL:/backup/private_media:ro")
  HAVE_VOL=1
fi
if [[ "$HAVE_VOL" -eq 1 ]]; then
  docker run --rm "${RUN_VOLS[@]}" -v "$WORK:/out" alpine:3.20 \
    tar czf /out/media.tgz -C /backup .
else
  MEDIA_ARGS=()
  [[ -d "$ROOT/media" ]] && MEDIA_ARGS+=(media)
  [[ -d "$ROOT/private_media" ]] && MEDIA_ARGS+=(private_media)
  if [[ ${#MEDIA_ARGS[@]} -gt 0 ]]; then
    tar czf "$WORK/media.tgz" -C "$ROOT" "${MEDIA_ARGS[@]}"
  else
    mkdir -p "$WORK/empty-media"
    tar czf "$WORK/media.tgz" -C "$WORK/empty-media" .
  fi
fi
test -s "$WORK/media.tgz"

cp "$BACKUP_ENV_FILE" "$WORK/config.env"

GIT_SHA="$(git -C "$ROOT" rev-parse --short HEAD 2>/dev/null || echo unknown)"
{
  echo "created_utc=${STAMP}"
  echo "hostname=$(hostname 2>/dev/null || echo unknown)"
  echo "git_sha=${GIT_SHA}"
  echo "compose_file=${BACKUP_COMPOSE_FILE}"
  echo "postgres_db=${POSTGRES_DB}"
  echo "postgres_user=${POSTGRES_USER}"
  echo "contents=db.dump,media.tgz,config.env"
} >"$WORK/MANIFEST"

echo "Encrypting with age..."
tar -C "$WORK" -cf - MANIFEST db.dump media.tgz config.env \
  | "$AGE_BIN" -R "$BACKUP_AGE_RECIPIENTS" -o "$WORK/$FILENAME"
test -s "$WORK/$FILENAME"

echo "Uploading s3://${BACKUP_S3_BUCKET}/${DAILY_KEY}"
aws_cli s3 cp "$WORK/$FILENAME" "s3://${BACKUP_S3_BUCKET}/${DAILY_KEY}"

MONTHLY_PREFIX="monthly/${MONTH}/"
if aws_cli s3 ls "s3://${BACKUP_S3_BUCKET}/${MONTHLY_PREFIX}" 2>/dev/null | grep -q .
then
  echo "Monthly snapshot for ${MONTH} already exists; skipping copy."
else
  echo "Uploading first monthly snapshot s3://${BACKUP_S3_BUCKET}/${MONTHLY_KEY}"
  aws_cli s3 cp "$WORK/$FILENAME" "s3://${BACKUP_S3_BUCKET}/${MONTHLY_KEY}"
fi

echo "OK $FILENAME"
echo "DAILY_KEY=${DAILY_KEY}"
echo "MONTHLY_KEY=${MONTHLY_KEY}"
