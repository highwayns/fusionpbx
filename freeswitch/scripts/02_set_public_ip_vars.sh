#!/usr/bin/env bash
set -euo pipefail

if [[ "${1:-}" == "" ]]; then
  echo "Usage: $0 <PUBLIC_IP>"
  exit 1
fi

PUB="$1"
FILE="/etc/freeswitch/vars.xml"

sudo cp -a "$FILE" "$FILE.bak.$(date +%Y%m%d%H%M%S)"

# Replace existing lines if present (best-effort)
sudo perl -0777 -i -pe "s|<X-PRE-PROCESS cmd=\"set\" data=\"external_sip_ip=.*?\"\s*/>|<X-PRE-PROCESS cmd=\"set\" data=\"external_sip_ip=${PUB}\"/>|g" "$FILE" || true
sudo perl -0777 -i -pe "s|<X-PRE-PROCESS cmd=\"set\" data=\"external_rtp_ip=.*?\"\s*/>|<X-PRE-PROCESS cmd=\"set\" data=\"external_rtp_ip=${PUB}\"/>|g" "$FILE" || true

echo "[OK] Updated $FILE. Now run:"
echo "  sudo fs_cli -x \"reloadxml\""
echo "  sudo fs_cli -x \"sofia profile restart all\""
