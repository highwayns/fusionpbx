## 3. 配置 dialplan：接听后启动音频流

### 3.1 放置 dialplan 文件
建议放：
- /etc/freeswitch/dialplan/default/ai_voicebot_9000.xml

示例见本包 `dialplan/ai_voicebot_9000.xml`。

### 3.2 reload dialplan
```bash
sudo fs_cli -x "reloadxml"
```

### 3.3 测试
- 用 softphone 注册到 FreeSWITCH（internal 或 external）
- 拨 9000
- 观察：
  - FreeSWITCH 日志：uuid_audio_stream 是否 start 成功
  - voice-gateway 日志：是否收到 metadata + 音频帧
