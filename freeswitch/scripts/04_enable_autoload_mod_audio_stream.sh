#!/usr/bin/env bash
set -euo pipefail

CONF="/etc/freeswitch/autoload_configs/modules.conf.xml"
sudo cp -a "$CONF" "$CONF.bak.$(date +%Y%m%d%H%M%S)"

if ! sudo grep -q 'mod_audio_stream' "$CONF"; then
  sudo perl -0777 -i -pe 's|(</modules>)|  <load module="mod_audio_stream"/>\n\1|s' "$CONF"
fi

echo "[OK] Updated $CONF. Now run:"
echo "  sudo fs_cli -x \"reloadxml\""
echo "  sudo fs_cli -x \"reload mod_audio_stream\""
