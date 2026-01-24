# Docker / Docker Compose (FreeSWITCH + mod_audio_stream)

这份 `step2_freeswitch` 包原本是面向 **Debian 12 裸机/VM** 的安装脚本与 Runbook。
我为它补齐了：

- `Dockerfile`：在容器内安装 FreeSWITCH（通过 `fsget`）并编译安装 `mod_audio_stream`
- `docker-compose.yml`：一键起 `freeswitch`（并提供可选的 `rasa` / `voice-gateway` 示例服务）

> 注：FreeSWITCH 的 Debian 包仓库需要 **SignalWire Personal Access Token (PAT)**。
> 官方文档说明了 `fsget` 的用法与该要求（见 SignalWire FreeSWITCH 文档的 Debian 安装页）。

---

## 1) 你需要“申请/准备”的东西（按常见场景）

### A. 仅在本机 Docker 自测（不接公网电话）
- Docker Engine + Docker Compose v2
- （可选）一个 WebSocket 语音网关服务（`mod_audio_stream` 会推音频到 `AUDIO_WS_URL`）

### B. 在云服务器/公网环境接入 SIP（推荐用于真实通话）
- 一台公网 VM（如 AWS EC2），建议绑定 **Elastic IP**（稳定公网 IP）
- **安全组 / 防火墙放通**（至少）：
  - SIP：`5060/udp,tcp` 与/或 `5080/udp,tcp`（具体以 Sofia profile 配置为准）
  - RTP：`16384-32768/udp`（媒体端口范围，必须放通）
  - （可选）Event Socket：`8021/tcp`（仅用于 `fs_cli` / ESL 调试）
- 一个 **SIP Trunk / DID**（例如 SignalWire / 其他运营商），或至少一个软电话（Zoiper/Linphone 等）

### C. 安装 FreeSWITCH Debian 包所需
- SignalWire **PAT**（Personal Access Token）
  - `fsget` 安装包时需要 `TOKEN=YOURSIGNALWIRETOKEN` 这类用法。

---

## 2) 关键运行时配置（必须理解的 3 个点）

### ① NAT / 公网 IP（云上强烈建议配置）
如果 FreeSWITCH 在 NAT 后面（云 VM + Docker 常见），请设置：

- `EXTERNAL_SIP_IP` = 你的公网 IP（或 EIP）
- `EXTERNAL_RTP_IP` = 你的公网 IP（或 EIP）

容器入口脚本会把它们写入 `/etc/freeswitch/vars.xml`。

### ② mod_audio_stream 的 WebSocket 目标
`dialplan/ai_voicebot_9000.xml` 默认会执行：

```
uuid_audio_stream start ... ws://.../ws
```

你需要提供一个能接收 WS 音频帧的服务（通常就是你的 voice-gateway），并用：

- `AUDIO_WS_URL=ws://voice-gateway:8080/ws`（容器内用服务名访问）

### ③ 端口映射与 RTP 端口范围
如果不用 `network_mode: host`，必须映射 RTP 端口段；否则会出现“能拨通但无声音/单向音”等问题。

---

## 3) 如何启动

### 方式 1：BuildKit secret（更安全，推荐）

1) 把 PAT 写入本地文件（不要提交到 Git）：

```
echo "YOUR_SIGNALWIRE_PAT" > .signalwire_pat
```

2) 启动：

```
DOCKER_BUILDKIT=1 docker build \
  --secret id=signalwire_pat,src=.signalwire_pat \
  -t mindoo-freeswitch:local .

docker compose up -d
```

### 方式 2：build-arg（不够安全，但最省事）

```
SIGNALWIRE_PAT=YOUR_SIGNALWIRE_PAT docker compose up -d --build
```

### 启动可选 Rasa 示例

```
docker compose --profile rasa up -d
```

Rasa 镜像版本示例使用 `rasa/rasa:3.6.20-full`（可按你的 Rasa 版本调整）。

---

## 4) 快速验证

1) 查看 FreeSWITCH 是否起来：

```
docker logs -f mindoo-freeswitch
```

2) 进入容器跑 `fs_cli`（如果你映射了 8021 且默认密码未改）：

```
docker exec -it mindoo-freeswitch fs_cli -rRS
```

3) 软电话拨 `9000`：
- 观察日志里是否出现 `uuid_audio_stream start ...`
- 观察 voice-gateway 是否收到 WebSocket 连接

---

## 5) 常见坑

- **容器架构非 amd64**：`mod_audio_stream` 编译时的 `FS_LIBS=/usr/lib/x86_64-linux-gnu` 需要改成你的架构路径。
- **无声音**：RTP 端口段未放通 / NAT 外部 IP 未设置 / 运营商对称 RTP。
- **WS 连接不上**：`AUDIO_WS_URL` 写成了 `127.0.0.1`（在容器里指向自己，而不是网关）。
