## 4. 验证清单（逐条打钩）

### 4.1 FreeSWITCH 基础
- [ ] `sudo fs_cli -rRS` 能进入
- [ ] `status` 显示正常
- [ ] `sofia status` 有 internal/external profile

### 4.2 NAT/公网变量
- [ ] vars.xml 设置了 external_sip_ip / external_rtp_ip = EIP
- [ ] `sofia profile restart all` 已执行

### 4.3 mod_audio_stream
- [ ] `module_exists mod_audio_stream` 返回 true
- [ ] 拨 9000 时，FreeSWITCH 日志里看到 uuid_audio_stream start
- [ ] voice-gateway 日志收到 metadata + bytes

### 4.4 无声/单向音频排查
- [ ] 安全组开放 RTP 端口范围（16384-32768/udp）
- [ ] SIP 入站端口与你实际使用的 profile 一致（5060 vs 5080）
