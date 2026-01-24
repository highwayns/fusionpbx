# Voice Gateway v2.0.0

AI呼叫中心 Voice Gateway - STT/TTS + Rasa/Dify + Mode Manager

## 🏗️ アーキテクチャ

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Voice Gateway アーキテクチャ                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   [FreeSWITCH] ──ESL──► [Voice Gateway]                                     │
│        │                      │                                              │
│        │                      ├─► [Transcribe] (STT)                        │
│        │                      ├─► [Polly] (TTS)                             │
│        │                      ├─► [Mode Manager] ◄── [Mindoo UI]            │
│        │                      │                                              │
│        │                      └─► [Rasa] ⇄ [Dify]                           │
│        │                              (NLU)    (LLM/RAG)                     │
│        │                                                                     │
│        └──SIP内部──► [Linphone坐席]                                          │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## ✨ 機能

### コア機能
- **WebSocket 音声ストリーム**: FreeSWITCH ESL 連携
- **Amazon Transcribe**: ストリーミング音声認識 (STT)
- **Amazon Polly**: 音声合成 (TTS)
- **Rasa 連携**: NLU / 対話管理（テキストのみ）
- **Dify 連携**: LLM + 知識庫 (RAG)

### Mode Manager
- **AI モード**: 自動応答（STT → Rasa/Dify → TTS）
- **Human モード**: 有人応答（坐席自動割当）
- **Transfer モード**: 特定坐席への転送

### REST API
- 通話管理 (`/calls/*`)
- モード切替 (`/calls/{id}/mode`)
- 坐席管理 (`/agents/*`)
- Rasa 連携 (`/rasa/*`)
- Dify 連携 (`/dify/*`)
- FreeSWITCH 制御 (`/freeswitch/*`)

## 🚀 クイックスタート

### 1. 環境設定

```bash
cp .env.example .env
# .env を編集して AWS 認証情報等を設定
```

### 2. 起動

```bash
# Voice Gateway のみ
docker-compose up -d

# フルスタック（FreeSWITCH + Rasa + Dify 含む）
docker-compose -f docker-compose.full.yml up -d
```

### 3. ヘルスチェック

```bash
curl http://localhost:8080/health
# OK

curl http://localhost:8080/health/detailed
# {"status": "ok", "services": {...}}
```

## 📡 API エンドポイント

### 通話管理

```bash
# 通話初期化
POST /calls/{call_id}/init

# 通話一覧
GET /calls

# 通話詳細
GET /calls/{call_id}

# 通話終了
DELETE /calls/{call_id}
```

### モード管理

```bash
# モード取得
GET /calls/{call_id}/mode
# Response: "ai" | "human" | "transfer"

# モード変更
PUT /calls/{call_id}/mode
# Body: {"mode": "ai" | "human" | "transfer", "agent": "agent-001"}

# 転送
POST /calls/{call_id}/transfer
# Body: {"target": "agent-001", "type": "blind"}
```

### 坐席管理

```bash
# 坐席一覧
GET /agents

# 空き坐席取得
GET /agents/available

# 坐席詳細
GET /agents/{agent_id}

# 坐席状態更新
PUT /agents/{agent_id}/status
# Body: {"status": "available" | "busy" | "wrap-up" | "offline"}
```

### Rasa 連携

```bash
# メッセージ送信
POST /rasa/message
# Body: {"sender": "caller-123", "message": "こんにちは"}

# 会話履歴取得
GET /rasa/conversations/{sender_id}

# NLU 解析のみ
POST /rasa/parse?message=こんにちは
```

### Dify 連携

```bash
# Chat API
POST /dify/chat
# Body: {"query": "製品について教えて", "conversation_id": "..."}

# Workflow 実行
POST /dify/workflow
# Body: {"query": "...", "intent": "product_inquiry"}
```

## 🔧 環境変数

| 変数 | デフォルト | 説明 |
|------|-----------|------|
| `AWS_REGION` | `ap-northeast-1` | AWS リージョン |
| `TRANSCRIBE_LANGUAGE_CODE` | `ja-JP` | 音声認識言語 |
| `POLLY_VOICE_ID` | `Takumi` | TTS 音声 |
| `RASA_URL` | `http://rasa:5005` | Rasa URL |
| `DIFY_API_URL` | `http://dify-api:5001/v1` | Dify API URL |
| `DIFY_API_KEY` | - | Dify API キー |
| `FREESWITCH_HOST` | `freeswitch` | FreeSWITCH ホスト |
| `FREESWITCH_PORT` | `8021` | FreeSWITCH ESL ポート |
| `FREESWITCH_PASSWORD` | `ClueCon` | FreeSWITCH ESL パスワード |

## 📁 ディレクトリ構成

```
voice-gateway/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI アプリケーション
│   ├── models.py            # データモデル
│   ├── state.py             # 状態管理
│   ├── mode_manager.py      # モード管理
│   ├── ws_handler.py        # WebSocket ハンドラ
│   ├── transcribe_service.py # Transcribe (STT)
│   ├── polly_service.py     # Polly (TTS)
│   ├── rasa_client.py       # Rasa クライアント
│   ├── dify_client.py       # Dify クライアント
│   └── esl_client.py        # FreeSWITCH ESL
├── .env.example
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── docker-compose.full.yml
└── README.md
```

## 🔄 データフロー

### AI 自動応答モード

```
顧客音声 → FreeSWITCH → Voice Gateway
                            ├→ Transcribe (STT) → テキスト
                            │                         ↓
                            │                      Rasa (NLU)
                            │                         ↓
                            │                      Dify (LLM)
                            │                         ↓
                            └← Polly (TTS) ← テキスト応答
                                   ↓
顧客 ← FreeSWITCH ← 音声応答
```

### 有人応答モード

```
Mindoo UI → PUT /calls/{id}/mode {"mode": "human"}
                     ↓
              Voice Gateway
                     ↓
              FreeSWITCH (転送)
                     ↓
              Linphone 坐席 ⇄ 顧客
```

## 📝 Swagger UI

http://localhost:8080/docs

## 🔒 セキュリティ

- 本番環境では TLS を有効化
- AWS IAM ポリシーで最小権限を設定
- FreeSWITCH ESL パスワードを変更
- Dify API キーを安全に管理

## 📄 ライセンス

MIT License
