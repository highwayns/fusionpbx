#!/usr/bin/env bash
set -euo pipefail

# This container expects FreeSWITCH configs under /etc/freeswitch (Debian packages).
# We patch a few runtime values from environment variables so the same image
# can run on local Docker, an EC2 VM, or behind NAT.

FS_CONF_DIR=${FS_CONF_DIR:-/etc/freeswitch}
DIALPLAN_FILE="$FS_CONF_DIR/dialplan/default/ai_voicebot_9000.xml"
VARS_FILE="$FS_CONF_DIR/vars.xml"

patch_vars_xml() {
  local k="$1" v="$2"
  [ -z "$v" ] && return 0
  if grep -q "data=\"$k=" "$VARS_FILE"; then
    # Replace value (any existing value up to the next quote)
    sed -i "s#data=\"$k=[^\"]*\"#data=\"$k=$v\"#" "$VARS_FILE" || true
  else
    # Insert before closing </include>
    sed -i "s#</include>#  <X-PRE-PROCESS cmd=\"set\" data=\"$k=$v\"/>\n</include>#" "$VARS_FILE"
  fi
}

patch_dialplan_ws_url() {
  local url="$1"
  [ -z "$url" ] && return 0
  if [ -f "$DIALPLAN_FILE" ]; then
    # Replace any existing ws/wss URL used by uuid_audio_stream
    sed -i "s#ws\(s\)\?://[^\"']\+/ws#${url}#g" "$DIALPLAN_FILE" || true
  fi
}

main() {
  # Patch external IPs if provided (recommended when running behind NAT / on cloud VMs)
  patch_vars_xml "external_sip_ip" "${EXTERNAL_SIP_IP:-}"
  patch_vars_xml "external_rtp_ip" "${EXTERNAL_RTP_IP:-}"

  # Patch websocket endpoint for mod_audio_stream
  patch_dialplan_ws_url "${AUDIO_WS_URL:-}"

  exec "$@"
}

main "$@"
