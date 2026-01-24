## Step3 总览

你将把 voice-gateway 部署到 Voice EC2（与 FreeSWITCH 同机），并只监听 127.0.0.1:8080：
- FreeSWITCH 侧 dialplan 已写死：ws://127.0.0.1:8080/ws
- 因此安全组不需要开放 8080

部署后验收：
1) `curl http://127.0.0.1:8080/health` 返回 OK
2) 拨 9000：能听到 TTS 回答（Rasa 不通也会返回兜底语）
