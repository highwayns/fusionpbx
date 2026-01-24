# Step2：Voice EC2（Debian 12）安装 FreeSWITCH + mod_audio_stream + dialplan（可复制版）

这份包把“第2步”落实为可操作的 Runbook + 脚本：
- 2.1 安装 FreeSWITCH（SignalWire PAT + fsget）
- 2.2 编译/安装 sptmru/mod_audio_stream（WS 音频推流与回放）
- 2.3 配 dialplan：接听后启动 uuid_audio_stream

适用：AWS EC2 Debian 12（x86_64）
