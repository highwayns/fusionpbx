#!/usr/bin/env bash
set -euo pipefail

SRC_DIR="$(cd "$(dirname "$0")"/.. && pwd)"
SRC="$SRC_DIR/dialplan/ai_voicebot_9000.xml"
DST="/etc/freeswitch/dialplan/default/ai_voicebot_9000.xml"

sudo cp -a "$SRC" "$DST"
echo "[OK] Installed dialplan to $DST"
echo "Now run: sudo fs_cli -x \"reloadxml\""
