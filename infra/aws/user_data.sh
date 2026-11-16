#!/bin/bash
# Launch script da VM Lightsail (roda como root na primeira inicialização).
# O registro no SSM vem depois, à mão: scripts/install-ssm-agent.sh com a activation.
# O Lightsail antepõe um cabeçalho e executa com sh: roda o corpo sob bash.
exec bash -s <<'IB_EOF'
set -euxo pipefail
export DEBIAN_FRONTEND=noninteractive

# 1 GB de RAM: swap de 2 GB para o build da imagem e picos do Postgres (ADR 0013).
if [ ! -f /swapfile ]; then
  fallocate -l 2G /swapfile
  chmod 600 /swapfile
  mkswap /swapfile
  swapon /swapfile
  echo '/swapfile none swap sw 0 0' >> /etc/fstab
fi
echo 'vm.swappiness=10' > /etc/sysctl.d/99-ib-conecta-swap.conf
sysctl -p /etc/sysctl.d/99-ib-conecta-swap.conf

apt-get update
apt-get install -y ca-certificates curl git

install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc

. /etc/os-release
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu ${VERSION_CODENAME} stable" > /etc/apt/sources.list.d/docker.list

apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin age unzip
usermod -aG docker ubuntu

case "$(uname -m)" in
  aarch64|arm64) awscli_arch="aarch64" ;;
  *) awscli_arch="x86_64" ;;
esac
tmp="$(mktemp -d)"
curl -fsSL "https://awscli.amazonaws.com/awscli-exe-linux-${awscli_arch}.zip" -o "$tmp/awscliv2.zip"
unzip -q "$tmp/awscliv2.zip" -d "$tmp"
"$tmp/aws/install" -i /usr/local/aws-cli -b /usr/local/bin
rm -rf "$tmp"
IB_EOF
