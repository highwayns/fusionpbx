## 2. 部署 voice-gateway（Debian 12）

### 2.1 放置目录
建议固定在：
- /opt/voice-gateway

```bash
sudo mkdir -p /opt/voice-gateway
sudo chown -R $USER:$USER /opt/voice-gateway
```

把本包里的内容拷贝到 /opt/voice-gateway（可用 scp/rsync）。

目录结构应是：
- /opt/voice-gateway/app/main.py
- /opt/voice-gateway/requirements.txt
- /opt/voice-gateway/.env

### 2.2 创建 venv & 安装依赖
```bash
cd /opt/voice-gateway
python3 -m venv venv
./venv/bin/pip install -U pip
./venv/bin/pip install -r requirements.txt
```

### 2.3 配置 .env
```bash
cp .env.example .env
nano .env
```

至少要改：
- RASA_REST_ENDPOINT（指向 Bot EC2 的私网 IP:5005）
- AWS_REGION（如果不是 ap-northeast-1）
- 语音参数（一般不用改）

### 2.4 安装 systemd
```bash
sudo cp systemd/voice-gateway.service /etc/systemd/system/voice-gateway.service
sudo systemctl daemon-reload
sudo systemctl enable --now voice-gateway
```

### 2.5 查看日志
```bash
sudo journalctl -u voice-gateway -f
```
