## 0. 前置条件（P0）

- 一台 EC2：Debian 12（建议 t3.medium 起步）
- 已分配 Elastic IP 并绑定到该实例（推荐）
- 安全组已开：
  - 22/tcp：仅你的公网 IP
  - 5060/udp（或 5080/udp，取决于 profile）：仅你的 IP 或 SIP Trunk IP
  - 16384-32768/udp：仅你的 IP 或 SIP Trunk IP
- 你有 SignalWire Personal Access Token（PAT）
  - FreeSWITCH Debian 包仓库需要 PAT 才能访问安装源
