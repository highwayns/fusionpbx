#!/usr/bin/env bash
set -euo pipefail

if [[ "${1:-}" == "" ]]; then
  echo "Usage: $0 <SIGNALWIRE_PAT>"
  exit 1
fi

TOKEN="$1"
sudo apt update
sudo apt install -y curl
curl -sSL https://freeswitch.org/fsget | bash -s "$TOKEN" release install

echo "[OK] Installed FreeSWITCH. Try: sudo fs_cli -rRS"
