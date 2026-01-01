# FusionPBX Docker 統合ガイド

## 📋 ファイル一覧

```
fusionpbx-docker/
├── Dockerfile              # FusionPBX コンテナ定義
├── nginx-fusionpbx.conf    # Nginx 設定
├── supervisord.conf        # プロセス管理設定
├── entrypoint.sh           # 起動スクリプト
├── docker-compose.yml      # 統合 Compose ファイル
├── .env.fusionpbx          # 環境変数サンプル
└── README.md               # このファイル
```

## 🚀 デプロイ手順

### Step 1: ファイルをコピー

```bash
# fusionpbx-docker ディレクトリをプロジェクトにコピー
cp -r fusionpbx-docker ~/sayama/

# 既存の docker-compose.yml をバックアップ
cd ~/sayama
cp docker-compose.yml docker-compose.yml.backup

# 新しい docker-compose.yml で置き換え
cp fusionpbx-docker/docker-compose.yml .
```

### Step 2: 環境変数を追加

```bash
# .env ファイルに FusionPBX 設定を追加
cat fusionpbx-docker/.env.fusionpbx >> .env
```

### Step 3: サービスをビルド・起動

```bash
# 既存サービスを停止
docker compose down

# FusionPBX を含む全サービスをビルド
docker compose build

# サービスを起動
docker compose up -d

# ログを確認
docker compose logs -f fusionpbx
```

### Step 4: FusionPBX 初期設定

1. ブラウザでアクセス: `http://your-server-ip/`
2. インストールウィザードが表示されます

#### データベース設定:
```
Database Type:    PostgreSQL
Database Host:    fusionpbx-db
Database Port:    5432
Database Name:    fusionpbx
Database User:    fusionpbx
Database Pass:    fusionpbx_secret_2024
```

#### 管理者アカウント:
```
Username:    admin
Password:    (強力なパスワードを設定)
```

#### FreeSWITCH ESL:
```
Event Socket Host:     freeswitch
Event Socket Port:     8021
Event Socket Password: ClueCon
```

## 🔧 voice-gateway 連携の設定

FusionPBX の GUI で AI ボット用ダイアルプランを追加:

1. **Dialplan** → **Dialplan Manager** → **Add**
2. 以下を設定:

```
Name:        AI Voice Bot
Number:      9000
Context:     default
Enabled:     true
Sequence:    100
```

Dialplan XML:
```xml
<extension name="ai_voicebot_9000">
  <condition field="destination_number" expression="^9000$">
    <action application="set" data="STREAM_SAMPLE_RATE=16000"/>
    <action application="set" data="api_on_answer=uuid_audio_stream ${uuid} start ws://voice-gateway:8080/ws mono 16k"/>
    <action application="answer"/>
    <action application="park"/>
  </condition>
</extension>
```

## 📊 サービス構成

```
┌─────────────────────────────────────────────────────────────┐
│                    Docker Network (pbx-network)             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐      ┌─────────────┐      ┌─────────────┐ │
│  │  FusionPBX  │      │  FreeSWITCH │      │voice-gateway│ │
│  │   :80/443   │─ESL─▶│   :5060     │─WS──▶│   :8080     │ │
│  └──────┬──────┘      │   :5080     │      └─────────────┘ │
│         │             │   :8021     │                       │
│         │             └─────────────┘                       │
│  ┌──────▼──────┐                                           │
│  │ PostgreSQL  │                                           │
│  │   :5432     │                                           │
│  └─────────────┘                                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 🔍 トラブルシューティング

### FusionPBX が起動しない
```bash
docker logs fusionpbx
docker exec fusionpbx nginx -t
```

### データベース接続エラー
```bash
docker exec fusionpbx-db psql -U fusionpbx -c "SELECT 1"
```

### FreeSWITCH ESL 接続確認
```bash
docker exec fusionpbx curl -s telnet://freeswitch:8021
```

### voice-gateway 接続確認
```bash
docker exec mindoo-freeswitch fs_cli -x "originate loopback/9000/default &park()"
docker logs --tail 20 mindoo-voice-gateway
```

## ⚠️ 注意事項

1. **ポート競合**: 80/443 が他のサービスで使用されている場合は変更が必要
2. **セキュリティ**: 本番環境では必ずパスワードを変更
3. **バックアップ**: 設定変更前にバックアップを取得

## 📞 サポートポート

| ポート | サービス | 用途 |
|--------|----------|------|
| 80     | FusionPBX | Web GUI (HTTP) |
| 443    | FusionPBX | Web GUI (HTTPS) |
| 5060   | FreeSWITCH | SIP シグナリング |
| 5080   | FreeSWITCH | SIP 外部プロファイル |
| 8021   | FreeSWITCH | ESL |
| 8080   | voice-gateway | WebSocket |
| 20000-20100 | FreeSWITCH | RTP メディア |

## パスワード関連問題と解決方法

cat >/var/www/fusionpbx/host.php <<'PHP'
<?php
header('Content-Type: text/plain');
echo "HTTP_HOST=" . ($_SERVER['HTTP_HOST'] ?? '') . "\n";
echo "SERVER_NAME=" . ($_SERVER['SERVER_NAME'] ?? '') . "\n";
PHP

http://localhost:8081/host.php


psql -h fusionpbx-db -U fusionpbx -d fusionpbx -c "update v_domains set domain_name='localhost' where domain_uuid='fdbf3399-5f98-478a-80c7-0ccd0562d88f';"
salt='fece803f-143d-4c91-b6ba-d798733b2cc3'
newpass='Zjhuen1915'   # ← 改成你想要的新密码
hash=$(php -r "echo md5('$salt'.'$newpass');")
echo "md5=[$hash] (len=${#hash})"
psql -h fusionpbx-db -U fusionpbx -d fusionpbx -c "update v_users set password='$hash' where username='admin';"
psql -h fusionpbx-db -U fusionpbx -d fusionpbx -tAX -c "select domain_uuid, domain_name from v_domains order by domain_name;"

http://localhost:8081/
ログイン:admin@localhost
パスワード:Zjhuen1915