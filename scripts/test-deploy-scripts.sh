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
out="$(scripts/deploy-prod-ssm.sh 2>&1)"
status=$?
set -e
printf '%s\n' "$out"
if [[ "$status" -eq 0 ]]; then
  echo "deploy-prod-ssm.sh deveria falhar sem SHA" >&2
  exit 1
fi

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

python3 -c "import pathlib; t=pathlib.Path('.github/workflows/deploy.yml').read_text(); assert 'id-token: write' in t; assert 'scripts/deploy-prod-ssm.sh' in t; assert 'scripts/test-deploy-scripts.sh' in t"

echo "OK test-deploy-scripts"
