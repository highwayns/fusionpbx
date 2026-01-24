#!/usr/bin/env bash
set -euo pipefail
cd /opt/voice-gateway
python3 -m venv venv
./venv/bin/pip install -U pip
./venv/bin/pip install -r requirements.txt
echo "[OK] venv ready"
