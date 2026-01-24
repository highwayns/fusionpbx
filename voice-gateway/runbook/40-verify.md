## 4. 验收（P0）

### 4.1 服务健康检查
```bash
curl -sS http://127.0.0.1:8080/health
```
期望输出：
- `OK`

### 4.2 Rasa 连通性（从 Voice EC2）
```bash
curl -sS -X POST "$RASA_REST_ENDPOINT" \
  -H 'Content-Type: application/json' \
  -d '{"sender":"health-test","message":"こんにちは"}'
```
应返回 JSON 数组（包含 text）。

### 4.3 实拨测试
- softphone 拨 9000（Step2 dialplan）
- 说一句日文，例如：『料金は？』
- 期望听到 TTS 回答（若 Rasa/Dify 未配置，会返回兜底语）

### 4.4 常见失败点
- IAM role 未绑定 -> Transcribe/Polly 报 AccessDenied
- TRANSCRIBE_SAMPLE_RATE 与 dialplan 不一致
- Bot EC2 的 5005 端口未允许来自 Voice EC2（安全组）
