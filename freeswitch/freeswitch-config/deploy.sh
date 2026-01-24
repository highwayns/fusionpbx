#!/bin/bash
#
# FreeSWITCH + SignalWire 設定デプロイスクリプト
# =============================================
# 使用方法: ./deploy.sh [container_name]
# 例: ./deploy.sh mindoo-freeswitch
#

set -e

# コンテナ名 (デフォルト: mindoo-freeswitch)
CONTAINER=${1:-mindoo-freeswitch}
FS_CLI="fs_cli -H127.0.0.1 -P8021 -pClueCon"

echo "=========================================="
echo "FreeSWITCH + SignalWire デプロイスクリプト"
echo "対象コンテナ: $CONTAINER"
echo "=========================================="

# 1. バックアップ
echo ""
echo "[1/6] 既存設定をバックアップ中..."
docker exec $CONTAINER bash -c "cp -r /etc/freeswitch /etc/freeswitch.bak.$(date +%Y%m%d_%H%M%S)" || true
echo "  ✓ バックアップ完了"

# 2. ディレクトリ確認
echo ""
echo "[2/6] ディレクトリ構造を確認中..."
docker exec $CONTAINER bash -c "mkdir -p /etc/freeswitch/sip_profiles/external"
docker exec $CONTAINER bash -c "mkdir -p /etc/freeswitch/dialplan/public"
docker exec $CONTAINER bash -c "mkdir -p /etc/freeswitch/dialplan/default"
echo "  ✓ ディレクトリ準備完了"

# 3. 設定ファイルをコピー
echo ""
echo "[3/6] 設定ファイルをコピー中..."

# SignalWire ゲートウェイ
docker cp ./sip_profiles/external/signalwire.xml \
  $CONTAINER:/etc/freeswitch/sip_profiles/external/
echo "  ✓ signalwire.xml"

# ダイアルプラン (public)
docker cp ./dialplan/public/00_signalwire_did_to_9000.xml \
  $CONTAINER:/etc/freeswitch/dialplan/public/
echo "  ✓ 00_signalwire_did_to_9000.xml"

# ダイアルプラン (default)
docker cp ./dialplan/default/09_voice_bot.xml \
  $CONTAINER:/etc/freeswitch/dialplan/default/
echo "  ✓ 09_voice_bot.xml"

echo "  ✓ すべてのファイルをコピー完了"

# 4. vars.xml NAT設定を追加
echo ""
echo "[4/6] vars.xml にNAT設定を追加中..."
docker exec $CONTAINER bash -c '
  if ! grep -q "external_sip_ip=126.19.122.165" /etc/freeswitch/vars.xml; then
    # </include> の前に挿入
    sed -i "/<\/include>/i\\
<!-- NAT Settings (SignalWire) -->\\
<X-PRE-PROCESS cmd=\"set\" data=\"external_sip_ip=126.19.122.165\"/>\\
<X-PRE-PROCESS cmd=\"set\" data=\"external_rtp_ip=126.19.122.165\"/>
" /etc/freeswitch/vars.xml
    echo "  ✓ NAT設定を追加しました"
  else
    echo "  - NAT設定は既に存在します"
  fi
'

# 5. 設定をリロード
echo ""
echo "[5/6] FreeSWITCH 設定をリロード中..."
docker exec $CONTAINER $FS_CLI -x "reloadxml"
echo "  ✓ XML リロード完了"

sleep 2

docker exec $CONTAINER $FS_CLI -x "sofia profile external restart"
echo "  ✓ Sofia external プロファイル再起動完了"

# 6. 状態確認
echo ""
echo "[6/6] ゲートウェイ状態を確認中..."
sleep 3
docker exec $CONTAINER $FS_CLI -x "sofia status gateway signalwire"

echo ""
echo "=========================================="
echo "デプロイ完了！"
echo ""
echo "次のステップ:"
echo "  1. 上記でゲートウェイが REGED になっていることを確認"
echo "  2. 携帯電話から +1-208-361-5909 へテスト発信"
echo "  3. 問題があれば: fs_cli -x 'sofia global siptrace on'"
echo "=========================================="
