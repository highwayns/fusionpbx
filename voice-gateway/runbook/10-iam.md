## 1. IAM（给 Voice EC2 的 Instance Profile）

P0 建议创建 Role：`MindooVoiceEc2Role`，并绑定到 Voice EC2。

最小策略（P0）：
- Transcribe Streaming（HTTP2 / WebSocket）
- Polly 合成

> 你也可以额外加 CloudWatchLogs 或 SSM（可选），本包先不强制。

### 1.1 策略 JSON（可直接复制）
保存为 `mindoo-voice-gateway-policy.json`，然后在 IAM 控制台创建并附加到 Role。

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "TranscribeStreaming",
      "Effect": "Allow",
      "Action": [
        "transcribe:StartStreamTranscription",
        "transcribe:StartStreamTranscriptionWebSocket"
      ],
      "Resource": "*"
    },
    {
      "Sid": "PollyTTS",
      "Effect": "Allow",
      "Action": [
        "polly:SynthesizeSpeech"
      ],
      "Resource": "*"
    }
  ]
}
```

### 1.2 绑定到 EC2
在 EC2 控制台：
- 实例 -> Actions -> Security -> Modify IAM role
- 选择 `MindooVoiceEc2Role`
