#!/bin/bash
set -euxo pipefail
export DEBIAN_FRONTEND=noninteractive

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

# Ubuntu 24.04 ARM no longer ships the awscli v1 package.
tmp="$(mktemp -d)"
curl -fsSL "https://awscli.amazonaws.com/awscli-exe-linux-aarch64.zip" -o "$tmp/awscliv2.zip"
unzip -q "$tmp/awscliv2.zip" -d "$tmp"
"$tmp/aws/install" -i /usr/local/aws-cli -b /usr/local/bin
rm -rf "$tmp"

# SSM Agent: GitHub Actions publica sem SSH inbound (docs/ops/deploy.md).
# Instâncias já existentes ignoram mudanças de user_data; nelas rode scripts/install-ssm-agent.sh.
tmp_ssm="$(mktemp -d)"
curl -fsSL "https://s3.amazonaws.com/ec2-downloads-windows/SSMAgent/latest/debian_arm64/amazon-ssm-agent.deb" -o "$tmp_ssm/amazon-ssm-agent.deb"
dpkg -i "$tmp_ssm/amazon-ssm-agent.deb"
rm -rf "$tmp_ssm"
systemctl enable --now amazon-ssm-agent
