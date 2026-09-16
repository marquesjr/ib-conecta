#!/usr/bin/env bash
# Instala o Amazon SSM Agent na VM de produção (Ubuntu). Rode uma vez, como root.
# Depois disso o GitHub Actions publica sem SSH. Ver docs/ops/deploy.md.
set -euo pipefail

if [[ "$(id -u)" -ne 0 ]]; then
  echo "rode como root: sudo scripts/install-ssm-agent.sh" >&2
  exit 1
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
systemctl enable --now amazon-ssm-agent
systemctl --no-pager --full status amazon-ssm-agent || true
echo "OK amazon-ssm-agent. Confira PingStatus=Online depois do attach da policy AmazonSSMManagedInstanceCore."
