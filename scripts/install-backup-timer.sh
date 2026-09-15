#!/usr/bin/env bash
# Install age, AWS CLI v2, and the daily systemd timer on the production VM.
set -euo pipefail

if [[ "$(id -u)" -ne 0 ]]; then
  echo "Run as root: sudo scripts/install-backup-timer.sh" >&2
  exit 1
fi

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
UNIT_DIR="$ROOT/scripts/backup/systemd"

export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y age unzip curl

install_awscliv2() {
  if command -v aws >/dev/null 2>&1; then
    return 0
  fi
  local tmp url
  tmp="$(mktemp -d)"
  case "$(uname -m)" in
    aarch64|arm64) url="https://awscli.amazonaws.com/awscli-exe-linux-aarch64.zip" ;;
    x86_64) url="https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" ;;
    *)
      echo "unsupported arch $(uname -m) for AWS CLI v2" >&2
      return 1
      ;;
  esac
  curl -fsSL "$url" -o "$tmp/awscliv2.zip"
  unzip -q "$tmp/awscliv2.zip" -d "$tmp"
  "$tmp/aws/install" -i /usr/local/aws-cli -b /usr/local/bin
  rm -rf "$tmp"
}

install_awscliv2

chmod 0755 "$ROOT/scripts/backup.sh" "$ROOT/scripts/restore.sh"
cp "$UNIT_DIR/ib-conecta-backup.service" /etc/systemd/system/ib-conecta-backup.service
cp "$UNIT_DIR/ib-conecta-backup.timer" /etc/systemd/system/ib-conecta-backup.timer
chmod 0644 /etc/systemd/system/ib-conecta-backup.service /etc/systemd/system/ib-conecta-backup.timer
rm -f /etc/systemd/system/ib-conecta-backup.time

if [[ ! -f "$ROOT/.env.backup" ]]; then
  echo "Create $ROOT/.env.backup from .env.backup.example before the first run." >&2
fi

systemctl daemon-reload
systemctl enable --now ib-conecta-backup.timer
systemctl list-timers ib-conecta-backup.timer --no-pager
echo "OK timer installed. Trigger once with: sudo systemctl start ib-conecta-backup.service"
