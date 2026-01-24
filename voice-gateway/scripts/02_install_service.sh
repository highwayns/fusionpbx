#!/usr/bin/env bash
set -euo pipefail
sudo cp /opt/voice-gateway/systemd/voice-gateway.service /etc/systemd/system/voice-gateway.service
sudo systemctl daemon-reload
sudo systemctl enable --now voice-gateway
echo "[OK] service started"
