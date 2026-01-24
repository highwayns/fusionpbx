## 2. 编译/安装 mod_audio_stream（sptmru）

### 2.1 安装依赖
```bash
sudo apt update
sudo apt install -y \
  git build-essential cmake pkg-config \
  libfreeswitch-dev libssl-dev zlib1g-dev libspeexdsp-dev
```

### 2.2 拉代码 & 编译安装
```bash
cd /usr/src
sudo git clone https://github.com/sptmru/freeswitch_mod_audio_stream.git
cd freeswitch_mod_audio_stream

sudo git submodule init
sudo git submodule update

mkdir -p build && cd build
cmake -DCMAKE_BUILD_TYPE=Release ..
make -j
sudo make install
```

### 2.3 加载模块（先手动，后自启）
手动加载：
```bash
sudo fs_cli -x "load mod_audio_stream"
sudo fs_cli -x "module_exists mod_audio_stream"
```

自启加载：
编辑 /etc/freeswitch/autoload_configs/modules.conf.xml
添加：
```xml
<load module="mod_audio_stream"/>
```

然后：
```bash
sudo fs_cli -x "reloadxml"
sudo fs_cli -x "reload mod_audio_stream"
```

### 2.4 音频流命令（你在 dialplan 会用到）
```text
uuid_audio_stream <uuid> start <ws-url> <mix-type> <sampling-rate> <metadata>
```
- ws-url：例如 ws://127.0.0.1:8080/ws
- mix-type：mono / mixed / stereo（P0 建议 mono）
- sampling-rate：建议 16k（ASR 更稳），模块会重采样
- metadata：JSON 字符串（建议带 call_uuid）
