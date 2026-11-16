#!/usr/bin/env bash
# Dispara o deploy de produção via AWS SSM Run Command (roda no GitHub Actions).
# Requer credenciais AWS já configuradas (OIDC) e aws + jq no PATH.
set -euo pipefail

AWS_REGION="${AWS_REGION:-us-east-2}"
INSTANCE_NAME="${INSTANCE_NAME:-ib-conecta-prod-app}"
DEPLOY_SHA="${1:-${DEPLOY_SHA:-}}"
POLL_SECONDS="${DEPLOY_POLL_SECONDS:-20}"
MAX_POLLS="${DEPLOY_MAX_POLLS:-90}"

if [[ -z "$DEPLOY_SHA" ]]; then
  echo "passe o SHA: $0 <40-hex>" >&2
  exit 1
fi
if [[ ! "$DEPLOY_SHA" =~ ^[0-9a-f]{40}$ ]]; then
  echo "DEPLOY_SHA inválido (esperado 40 hex): $DEPLOY_SHA" >&2
  exit 1
fi

# AWS-RunShellScript + JSON flatten newlines. A multiline `bash -lc $(printf %q "$INNER")`
# turned `>/dev/null\ngit` into `/dev/nullngit` (run 35142349685). Keep this ONE line.
REMOTE="sudo -u ubuntu -H env DEPLOY_SHA=${DEPLOY_SHA} bash -c 'set -euo pipefail; cd /home/ubuntu/ib-conecta; git fetch --prune origin master; git checkout -B master \"\$DEPLOY_SHA\"; exec bash scripts/deploy-prod.sh'"

if [[ "${DEPLOY_SSM_PRINT_REMOTE:-}" == "1" ]]; then
  printf '%s\n' "$REMOTE"
  exit 0
fi

if ! command -v aws >/dev/null 2>&1; then
  echo "aws CLI não encontrado" >&2
  exit 1
fi
if ! command -v jq >/dev/null 2>&1; then
  echo "jq não encontrado" >&2
  exit 1
fi

# A VM é uma managed instance híbrida do SSM (Lightsail, ADR 0013): o Name vem da activation.
echo "região $AWS_REGION — procurando managed instance Name=$INSTANCE_NAME"
NODES="$(aws ssm describe-instance-information \
  --region "$AWS_REGION" \
  --output json \
  | jq -c --arg name "$INSTANCE_NAME" \
    '[.InstanceInformationList[] | select(.Name == $name) | {id: .InstanceId, ping: .PingStatus}]')"
mapfile -t INSTANCE_IDS < <(jq -r '.[] | select(.ping == "Online") | .id' <<<"$NODES")

if [[ "${#INSTANCE_IDS[@]}" -ne 1 ]]; then
  echo "esperado 1 managed instance Online com Name=$INSTANCE_NAME, achei ${#INSTANCE_IDS[@]}." >&2
  echo "Registradas com esse Name: $NODES" >&2
  echo "Registro da VM e limpeza de nós antigos: docs/ops/deploy.md" >&2
  exit 1
fi
INSTANCE_ID="${INSTANCE_IDS[0]}"
echo "instância $INSTANCE_ID"

PAYLOAD="$(jq -n \
  --arg instance "$INSTANCE_ID" \
  --arg comment "ib-conecta deploy ${DEPLOY_SHA}" \
  --arg cmd "$REMOTE" \
  '{
    DocumentName: "AWS-RunShellScript",
    InstanceIds: [$instance],
    TimeoutSeconds: 1800,
    Comment: $comment,
    CloudWatchOutputConfig: { CloudWatchOutputEnabled: false },
    Parameters: {
      commands: [$cmd],
      executionTimeout: ["1800"]
    }
  }')"

COMMAND_ID="$(aws ssm send-command \
  --region "$AWS_REGION" \
  --cli-input-json "$PAYLOAD" \
  --query 'Command.CommandId' \
  --output text)"
echo "ssm command $COMMAND_ID"

STATUS="Pending"
for _ in $(seq 1 "$MAX_POLLS"); do
  STATUS="$(aws ssm get-command-invocation \
    --region "$AWS_REGION" \
    --command-id "$COMMAND_ID" \
    --instance-id "$INSTANCE_ID" \
    --query 'Status' \
    --output text 2>/dev/null || echo "Pending")"
  echo "ssm status $STATUS"
  case "$STATUS" in
    Success|Failed|Cancelled|TimedOut|Cancelling|Undeliverable|Terminated)
      break
      ;;
    *)
      sleep "$POLL_SECONDS"
      ;;
  esac
done

INVOCATION="$(aws ssm get-command-invocation \
  --region "$AWS_REGION" \
  --command-id "$COMMAND_ID" \
  --instance-id "$INSTANCE_ID" \
  --output json)"
echo "$INVOCATION" | jq -r '"status=" + .Status + " details=" + (.StatusDetails // "")'
echo "----- stdout -----"
echo "$INVOCATION" | jq -r '.StandardOutputContent // ""'
echo "----- stderr -----"
echo "$INVOCATION" | jq -r '.StandardErrorContent // ""'

if [[ "$STATUS" != "Success" ]]; then
  echo "deploy SSM falhou ($STATUS). Runbook: docs/ops/deploy.md" >&2
  exit 1
fi
echo "OK ssm deploy $DEPLOY_SHA"
