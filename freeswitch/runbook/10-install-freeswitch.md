## 1. 安装 FreeSWITCH（Debian 12，fsget）

### 1.1 执行安装
```bash
TOKEN="你的SignalWirePAT"

sudo apt update
sudo apt install -y curl
curl -sSL https://freeswitch.org/fsget | bash -s "$TOKEN" release install
```

### 1.2 验证
```bash
sudo fs_cli -rRS
# 在 fs_cli 里：
# status
```

### 1.3（强烈建议）配置公网 IP / NAT 变量
如果你绑定了 EIP，建议写死 external_sip_ip / external_rtp_ip，避免单向音频/无声。

编辑：
- /etc/freeswitch/vars.xml

把下面两行设置为“实例公网 IP（EIP）”：
```xml
<X-PRE-PROCESS cmd="set" data="external_sip_ip=你的公网IP"/>
<X-PRE-PROCESS cmd="set" data="external_rtp_ip=你的公网IP"/>
```

然后：
```bash
sudo fs_cli -x "reloadxml"
sudo fs_cli -x "sofia profile restart all"
```

### 1.4 端口提醒（external profile 默认 5080）
如果你对接 SIP Trunk，多数会用 external profile，默认端口常为 5080。
你需要确认你的 trunk/softphone 实际打到哪个端口，并相应放行安全组。
