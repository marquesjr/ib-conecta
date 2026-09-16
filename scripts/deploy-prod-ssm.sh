#!/usr/bin/env bash
# Dispara o deploy de produção via AWS SSM Run Command (roda no GitHub Actions).
# Requer credenciais AWS já configuradas (OIDC) e aws + jq no PATH.
set -euo pipefail

AWS_REGION="${AWS_REGION:-us-east-2}"
INSTANCE_NAME_TAG="${INSTANCE_NAME_TAG:-ib-conecta-prod-app}"
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

if ! command -v aws >/dev/null 2>&1; then
  echo "aws CLI não encontrado" >&2
  exit 1
fi
if ! command -v jq >/dev/null 2>&1; then
  echo "jq não encontrado" >&2
  exit 1
fi

echo "região $AWS_REGION — procurando instância Name=$INSTANCE_NAME_TAG"
mapfile -t INSTANCE_IDS < <(aws ec2 describe-instances \
  --region "$AWS_REGION" \
  --filters \
    "Name=tag:Name,Values=${INSTANCE_NAME_TAG}" \
    "Name=instance-state-name,Values=running" \
  --query 'Reservations[].Instances[].InstanceId' \
  --output text | tr '\t' '\n' | sed '/^$/d')

if [[ "${#INSTANCE_IDS[@]}" -ne 1 ]]; then
  echo "esperado 1 instância running com Name=$INSTANCE_NAME_TAG, achei ${#INSTANCE_IDS[@]} (${INSTANCE_IDS[*]:-nenhuma})" >&2
  exit 1
fi
INSTANCE_ID="${INSTANCE_IDS[0]}"
echo "instância $INSTANCE_ID"

PING="$(aws ssm describe-instance-information \
  --region "$AWS_REGION" \
  --filters "Key=InstanceIds,Values=${INSTANCE_ID}" \
  --query 'InstanceInformationList[0].PingStatus' \
  --output text)"
if [[ "$PING" != "Online" ]]; then
  echo "SSM não está Online nesta instância (PingStatus=${PING})." >&2
  echo "Na VM: sudo scripts/install-ssm-agent.sh  — e confira docs/ops/deploy.md" >&2
  exit 1
fi

INNER="set -euo pipefail
cd /home/ubuntu/ib-conecta
git fetch --prune origin master
git rev-parse --verify ${DEPLOY_SHA}^{commit} >/dev/null
git checkout -B master ${DEPLOY_SHA}
exec bash scripts/deploy-prod.sh"
REMOTE="sudo -u ubuntu -H env DEPLOY_SHA=${DEPLOY_SHA} bash -lc $(printf '%q' "$INNER")"

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
