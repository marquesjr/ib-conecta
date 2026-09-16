#!/usr/bin/env bash
# Instala ou habilita o Amazon SSM Agent na VM de produção (Ubuntu). Rode uma vez, como root.
# A EC2 atual traz o agente via snap (classic); o .deb recusa o preinst nesse caso.
# Depois disso o GitHub Actions publica sem SSH. Ver docs/ops/deploy.md.
set -euo pipefail

SNAP_UNIT="snap.amazon-ssm-agent.amazon-ssm-agent.service"
DEB_UNIT="amazon-ssm-agent.service"

if [[ "$(id -u)" -ne 0 ]]; then
  echo "rode como root: sudo scripts/install-ssm-agent.sh" >&2
  exit 1
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

if snap_owns_agent; then
  echo "amazon-ssm-agent já está no snap; pulando o pacote .deb (o preinst do dpkg recusa)."
  if ! enable_start "$SNAP_UNIT"; then
    echo "falha ao iniciar $SNAP_UNIT" >&2
    systemctl --no-pager --full status "$SNAP_UNIT" || true
    exit 1
  fi
  systemctl --no-pager --full status "$SNAP_UNIT" || true
  echo "OK $SNAP_UNIT. Reinício: sudo systemctl restart ${SNAP_UNIT%.service}"
  echo "Confira PingStatus=Online depois do attach da policy AmazonSSMManagedInstanceCore."
  exit 0
fi

export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y ca-certificates curl

ARCH="$(dpkg --print-architecture)"
case "$ARCH" in
  arm64) DEB_ARCH="debian_arm64" ;;
  amd64) DEB_ARCH="debian_amd64" ;;
  *)
    echo "arquitetura não suportada: $ARCH" >&2
    exit 1
    ;;
esac

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
curl -fsSL "https://s3.amazonaws.com/ec2-downloads-windows/SSMAgent/latest/${DEB_ARCH}/amazon-ssm-agent.deb" \
  -o "$tmp/amazon-ssm-agent.deb"
dpkg -i "$tmp/amazon-ssm-agent.deb"
enable_start "$DEB_UNIT"
systemctl --no-pager --full status "$DEB_UNIT" || true
echo "OK $DEB_UNIT. Confira PingStatus=Online depois do attach da policy AmazonSSMManagedInstanceCore."
