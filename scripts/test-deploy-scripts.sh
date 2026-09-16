#!/usr/bin/env bash
# Checagens estáticas dos scripts de deploy (job verify da Action e uso local).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

bash -n scripts/deploy-prod.sh
bash -n scripts/deploy-prod-ssm.sh
bash -n scripts/install-ssm-agent.sh
bash -n scripts/test-deploy-scripts.sh

chmod +x scripts/deploy-prod.sh scripts/deploy-prod-ssm.sh scripts/install-ssm-agent.sh

set +e
out="$(scripts/deploy-prod.sh 2>&1)"
status=$?
set -e
printf '%s\n' "$out"
if [[ "$status" -eq 0 ]]; then
  echo "deploy-prod.sh deveria falhar sem .env.prod" >&2
  exit 1
fi
printf '%s\n' "$out" | grep -q '\.env\.prod'

set +e
out="$(env -u GITHUB_SHA -u DEPLOY_SHA scripts/deploy-prod-ssm.sh 2>&1)"
status=$?
set -e
printf '%s\n' "$out"
if [[ "$status" -eq 0 ]]; then
  echo "deploy-prod-ssm.sh deveria falhar sem SHA" >&2
  exit 1
fi
printf '%s\n' "$out" | grep -q 'passe o SHA'

set +e
out="$(scripts/deploy-prod-ssm.sh deadbeef 2>&1)"
status=$?
set -e
printf '%s\n' "$out"
if [[ "$status" -eq 0 ]]; then
  echo "deploy-prod-ssm.sh deveria rejeitar SHA curto" >&2
  exit 1
fi
printf '%s\n' "$out" | grep -qi 'inválido\|invalido'

sha="$(git rev-parse HEAD)"
remote="$(DEPLOY_SSM_PRINT_REMOTE=1 scripts/deploy-prod-ssm.sh "$sha")"
printf '%s\n' "$remote"
if grep -E 'nullngit|/dev/nulln' <<<"$remote"; then
  echo "comando SSM colou newline em /dev/null" >&2
  exit 1
fi
if [[ "$remote" == *$'\n'* ]]; then
  echo "comando SSM deve ser uma linha só" >&2
  exit 1
fi
grep -q "DEPLOY_SHA=${sha}" <<<"$remote"
grep -q "scripts/deploy-prod.sh" <<<"$remote"
echo "ssm remote command ok"

python3 - <<'PY'
from pathlib import Path

workflow = Path(".github/workflows/deploy.yml").read_text()
assert "id-token: write" in workflow
assert "audience: sts.amazonaws.com" in workflow
assert "scripts/deploy-prod-ssm.sh" in workflow
assert "scripts/test-deploy-scripts.sh" in workflow
tf = Path("infra/aws/deploy.tf").read_text()
assert "repo:marquesjr@2216233/ib-conecta@1314311915" in Path("infra/aws/variables.tf").read_text()
assert "local.github_oidc_sub_master" in tf
assert "token.actions.githubusercontent.com:aud" in tf
assert "sts.amazonaws.com" in tf
print("oidc assertions ok")

install = Path("scripts/install-ssm-agent.sh").read_text()
assert "snap.amazon-ssm-agent.amazon-ssm-agent.service" in install
assert "pulando o pacote .deb" in install
assert "snap list amazon-ssm-agent" in install
docs = Path("docs/ops/deploy.md").read_text()
assert "snap.amazon-ssm-agent.amazon-ssm-agent" in docs
assert "pula o .deb" in docs
print("snap-unit assertions ok")
PY

echo "OK test-deploy-scripts"
