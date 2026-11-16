#!/usr/bin/env bash
# Instala o Amazon SSM Agent na VM de produção (Ubuntu) e, no Lightsail, registra a VM
# como managed instance híbrida. Rode uma vez, como root. Ver docs/ops/deploy.md.
#
#   sudo SSM_ACTIVATION_ID=... SSM_ACTIVATION_CODE=... scripts/install-ssm-agent.sh
#
# Os valores vêm de `terraform output ssm_activation_id` e
# `terraform output -raw ssm_activation_code` (infra/aws). Sem eles o script só
# instala e liga o agente (caso de EC2 com instance profile).
#
# Imagens Ubuntu da AWS trazem o agente via snap (classic); o .deb recusa o preinst
# nesse caso, então o script usa o snap quando ele existe.
set -euo pipefail

SNAP_UNIT="snap.amazon-ssm-agent.amazon-ssm-agent.service"
DEB_UNIT="amazon-ssm-agent.service"
SNAP_BIN="/snap/amazon-ssm-agent/current/amazon-ssm-agent"
DEB_BIN="/usr/bin/amazon-ssm-agent"
REGION="${SSM_REGION:-us-east-2}"

if [[ "$(id -u)" -ne 0 ]]; then
  echo "rode como root: sudo scripts/install-ssm-agent.sh" >&2
  exit 1
fi

if [[ -n "${SSM_ACTIVATION_ID:-}" || -n "${SSM_ACTIVATION_CODE:-}" ]]; then
  if [[ -z "${SSM_ACTIVATION_ID:-}" || -z "${SSM_ACTIVATION_CODE:-}" ]]; then
    echo "informe SSM_ACTIVATION_ID e SSM_ACTIVATION_CODE juntos" >&2
    exit 1
  fi
fi

snap_owns_agent() {
  if command -v snap >/dev/null 2>&1 && snap list amazon-ssm-agent >/dev/null 2>&1; then
    return 0
  fi
  if [[ -d /snap/amazon-ssm-agent ]] || systemctl cat "$SNAP_UNIT" >/dev/null 2>&1; then
    return 0
  fi
  return 1
}

enable_start() {
  local unit="$1"
  local _
  # Units do snap costumam já estar "enabled"; o enable pode falhar sem impedir o start.
  systemctl enable "$unit" >/dev/null 2>&1 || true
  systemctl start "$unit"
  for _ in 1 2 3 4 5; do
    if systemctl is-active --quiet "$unit"; then
      return 0
    fi
    sleep 1
  done
  return 1
}

install_deb() {
  export DEBIAN_FRONTEND=noninteractive
  apt-get update
  apt-get install -y ca-certificates curl

  local arch deb_arch tmp
  arch="$(dpkg --print-architecture)"
  case "$arch" in
    arm64) deb_arch="debian_arm64" ;;
    amd64) deb_arch="debian_amd64" ;;
    *)
      echo "arquitetura não suportada: $arch" >&2
      exit 1
      ;;
  esac

  tmp="$(mktemp -d)"
  curl -fsSL "https://s3.amazonaws.com/ec2-downloads-windows/SSMAgent/latest/${deb_arch}/amazon-ssm-agent.deb" \
    -o "$tmp/amazon-ssm-agent.deb"
  dpkg -i "$tmp/amazon-ssm-agent.deb"
  rm -rf "$tmp"
}

if snap_owns_agent; then
  echo "amazon-ssm-agent já está no snap; pulando o pacote .deb (o preinst do dpkg recusa)."
  UNIT="$SNAP_UNIT"
  AGENT_BIN="$SNAP_BIN"
else
  install_deb
  UNIT="$DEB_UNIT"
  AGENT_BIN="$DEB_BIN"
fi

if [[ -n "${SSM_ACTIVATION_ID:-}" ]]; then
  echo "registrando a VM no SSM (activation ${SSM_ACTIVATION_ID}, região ${REGION})"
  systemctl stop "$UNIT" || true
  # -y sobrescreve um registro anterior (VM que já foi EC2 ou activation refeita).
  "$AGENT_BIN" -register -y \
    -code "$SSM_ACTIVATION_CODE" \
    -id "$SSM_ACTIVATION_ID" \
    -region "$REGION"
fi

if ! enable_start "$UNIT"; then
  echo "falha ao iniciar $UNIT" >&2
  systemctl --no-pager --full status "$UNIT" || true
  exit 1
fi
systemctl --no-pager --full status "$UNIT" || true

if [[ -f /var/lib/amazon/ssm/registration ]]; then
  echo "registro híbrido: $(cat /var/lib/amazon/ssm/registration)"
fi
echo "OK $UNIT. Reinício: sudo systemctl restart ${UNIT%.service}"
echo "Confira PingStatus=Online em aws ssm describe-instance-information (docs/ops/deploy.md)."
