## 3. 关键参数解释（必须理解的坑位）

### 3.1 Transcribe 的采样率必须和“输入音频实际采样率”一致
- 你在 dialplan 里启动 uuid_audio_stream 时指定了 16k
- 因此 TRANSCRIBE_SAMPLE_RATE 必须是 16000
如果你把 dialplan 改成 8k，那么 TRANSCRIBE_SAMPLE_RATE 也要改 8000（否则识别会明显变差/异常）。

### 3.2 Polly 输出采样率建议 8000（电话回放最稳）
- POLLY_SAMPLE_RATE=8000
- 返回的是 16-bit mono little-endian PCM（raw）
- 我们通过 streamAudio 回给 mod_audio_stream 播放

### 3.3 AUDIO_QUEUE_MAX（低延迟优先）
- 音频进入队列，如果队列满会丢帧（宁愿丢也不要积压导致延迟爆炸）
