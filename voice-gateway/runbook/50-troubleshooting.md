## 5. 排障速查

### 5.1 没有任何识别结果
- 检查 dialplan 的 uuid_audio_stream 是否 start 成功
  - `sudo journalctl -u freeswitch -f` 或 FreeSWITCH console
- 检查 voice-gateway 是否收到 bytes
  - `sudo journalctl -u voice-gateway -f` 里应看到连接建立

### 5.2 识别有，但不回话
- RASA_REST_ENDPOINT 配错/不通
- Bot EC2 安全组未允许 Voice EC2 访问 5005

### 5.3 回话了，但电话里听不到
- Polly 失败（检查 IAM）
- sampleRate 不匹配（建议 Polly 用 8000）
- mod_audio_stream 未加载或 WS 回包格式不对（type=streamAudio）
