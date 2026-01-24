#!/usr/bin/env bash
set -euo pipefail

sudo apt update
sudo apt install -y   git build-essential cmake pkg-config   libfreeswitch-dev libssl-dev zlib1g-dev libspeexdsp-dev

cd /usr/src
if [[ ! -d freeswitch_mod_audio_stream ]]; then
  sudo git clone https://github.com/sptmru/freeswitch_mod_audio_stream.git
fi
cd freeswitch_mod_audio_stream
sudo git submodule init
sudo git submodule update

mkdir -p build
cd build
cmake -DCMAKE_BUILD_TYPE=Release ..
make -j
sudo make install

echo "[OK] Installed mod_audio_stream. Now load it:"
echo "  sudo fs_cli -x \"load mod_audio_stream\""
