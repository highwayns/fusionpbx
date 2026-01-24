# FreeSWITCH + SignalWire 設定デプロイガイド

## 📁 ファイル構成

```
freeswitch-config/
├── sip_profiles/
│   ├── external.xml                    # 外部SIPプロファイル (NAT対応)
│   └── external/
│       └── signalwire.xml              # SignalWire ゲートウェイ
├── dialplan/
│   ├── public/
│   │   └── 00_signalwire_did_to_9000.xml   # DID着信ルーティング
│   └── default/
│       └── 09_voice_bot.xml            # 音声ボット (9000)
├── autoload_configs/
│   ├── acl.conf.xml                    # アクセス制御リスト
│   └── switch-conf-rtp-settings.xml    # RTPポート設定
└── vars-nat-additions.xml              # NAT変数設定
```

---

## 🚀 デプロイ手順

### Step 1: バックアップ

```bash
# 既存設定をバックアップ
docker exec mindoo-freeswitch bash -c "cp -r /etc/freeswitch /etc/freeswitch.bak"
```

### Step 2: 設定ファイルをコピー

```bash
# ゲートウェイ設定
docker cp ./sip_profiles/external/signalwire.xml \
  mindoo-freeswitch:/etc/freeswitch/sip_profiles/external/

# 外部プロファイル (必要に応じて)
docker cp ./sip_profiles/external.xml \
  mindoo-freeswitch:/etc/freeswitch/sip_profiles/

# ダイアルプラン (public)
docker cp ./dialplan/public/00_signalwire_did_to_9000.xml \
  mindoo-freeswitch:/etc/freeswitch/dialplan/public/

# ダイアルプラン (default)
docker cp ./dialplan/default/09_voice_bot.xml \
  mindoo-freeswitch:/etc/freeswitch/dialplan/default/
```

### Step 3: vars.xml にNAT設定を追加

```bash
docker exec -it mindoo-freeswitch bash

# vars.xml を編集
vi /etc/freeswitch/vars.xml

# 以下を追加 (</include> の前):
# <X-PRE-PROCESS cmd="set" data="external_sip_ip=126.19.122.165"/>
# <X-PRE-PROCESS cmd="set" data="external_rtp_ip=126.19.122.165"/>
```

### Step 4: 設定をリロード

```bash
# XMLリロード
fs_cli -H127.0.0.1 -P8021 -pClueCon -x "reloadxml"

# Sofiaプロファイル再起動
fs_cli -H127.0.0.1 -P8021 -pClueCon -x "sofia profile external restart"
```

---

## ✅ 検証手順

### 1. ゲートウェイ登録確認

```bash
fs_cli -H127.0.0.1 -P8021 -pClueCon -x "sofia status gateway signalwire"
```

**期待結果:** `State: REGED`

### 2. ダイアルプラン確認

```bash
fs_cli -H127.0.0.1 -P8021 -pClueCon -x "show dialplan public"
```

### 3. 内部テスト (AI音声ボット)

```bash
docker exec -it mindoo-freeswitch fs_cli -H127.0.0.1 -P8021 -pClueCon -x \
  "originate loopback/9000/default/XML &park()"
```

### 4. 外部テスト (電話発信)

携帯電話から `+1-208-361-5909` へ発信し、音声ボットが応答することを確認。

---

## 🔧 トラブルシューティング

### 登録失敗 (401/403)

```bash
# SIPトレース有効化
fs_cli -x "sofia global siptrace on"

# ログ確認
tail -f /var/log/freeswitch/freeswitch.log | grep signalwire
```

**チェックポイント:**
- ユーザー名/パスワード
- SIPドメイン
- トランスポート (UDP/TLS)

### 音声なし / 片通話

```bash
# RTPポート確認
ss -lnup | grep -E "20[0-9]{3}"

# パケットキャプチャ
tcpdump -i any port 20000-20100 -n
```

**チェックポイント:**
- RTPポートマッピング (ルーター)
- external_rtp_ip 設定
- SIP ALG 無効化

### 30秒で切断

NATセッションタイムアウトの可能性。

```bash
# pingを短縮 (signalwire.xml)
<param name="ping" value="15"/>

# 登録期限を短縮
<param name="expire-seconds" value="180"/>
```

---

## 📋 設定値サマリー

| 項目 | 値 |
|------|-----|
| 公网IP | 126.19.122.165 |
| SIPポート (external) | 5080/UDP |
| SIPポート (internal) | 5060/UDP |
| RTPポート範囲 | 20000-20100/UDP |
| SignalWire SIP Domain | highwayns-13dced887019.sip.signalwire.com |
| SIP Endpoint Username | tei952 |
| DID | +12083615909 |
| ゲートウェイ名 | signalwire |
| 着信ルート先 | 9000 (XML default) |
| Voice Gateway WS | ws://voice-gateway:8080/ws |
| Rasa Endpoint | http://rasa:5005/webhooks/rest/webhook |

---

## 🛡️ セキュリティ推奨事項

1. **SIPポート変更**: 5060/5080 → 高位ポート (例: 15060)
2. **ACL設定**: SignalWire IPのみ許可
3. **fail2ban**: SIP攻撃対策
4. **TLS/SRTP**: 接続確認後に有効化
5. **定期的なパスワード変更**

---

## 📞 コマンドクイックリファレンス

```bash
# ゲートウェイ状態
fs_cli -x "sofia status gateway signalwire"

# 通話一覧
fs_cli -x "show calls"

# 全通話切断
fs_cli -x "hupall"

# SIPトレース
fs_cli -x "sofia global siptrace on"

# 設定リロード
fs_cli -x "reloadxml"

# プロファイル再起動
fs_cli -x "sofia profile external restart"
```
