# syntax=docker/dockerfile:1.6

ARG DEBIAN_VERSION=bookworm
FROM debian:${DEBIAN_VERSION}

# Build-time args
ARG SIGNALWIRE_PAT=
ARG FS_CHANNEL=release
ARG FS_ACTION=install
ARG FS_META_PACKAGE=freeswitch-meta-all

# Runtime envs
ENV DEBIAN_FRONTEND=noninteractive \
    AUDIO_WS_URL=ws://voice-gateway:8080/ws \
    EXTERNAL_SIP_IP= \
    EXTERNAL_RTP_IP=

# --- OS deps ---
RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
      ca-certificates curl gnupg2 \
      git gcc g++ make cmake pkg-config \
      libssl-dev libspeexdsp-dev zlib1g-dev libevent-dev; \
    rm -rf /var/lib/apt/lists/*

# --- Install FreeSWITCH via fsget (requires SignalWire PAT) ---
# Security note:
# - Preferred: BuildKit secret: docker build --secret id=signalwire_pat,src=./.signalwire_pat
# - Fallback: build-arg SIGNALWIRE_PAT=... (less secure; may be stored in build history)
RUN --mount=type=secret,id=signalwire_pat,required=false \
    set -eux; \
    PAT="${SIGNALWIRE_PAT}"; \
    if [ -f /run/secrets/signalwire_pat ]; then PAT="$(cat /run/secrets/signalwire_pat)"; fi; \
    if [ -z "${PAT}" ]; then \
      echo "ERROR: Missing SignalWire PAT. Provide build-arg SIGNALWIRE_PAT or BuildKit secret signalwire_pat."; \
      exit 1; \
    fi; \
    apt-get update; \
    apt-get install -y --no-install-recommends curl; \
    curl -sSL https://freeswitch.org/fsget | bash -s "${PAT}" "${FS_CHANNEL}" "${FS_ACTION}"; \
    # Ensure headers/libs exist for building external modules
    apt-get update; \
    apt-get install -y --no-install-recommends libfreeswitch-dev; \
    rm -rf /var/lib/apt/lists/*

# --- Build & install mod_audio_stream ---
# NOTE:
# The upstream project moved to a CMake build (no top-level Makefile).
# See README "Building": mkdir build && cd build && cmake .. && make && make install.
RUN set -eux; \
    git clone --depth 1 https://github.com/amigniter/mod_audio_stream.git /usr/src/mod_audio_stream; \
    cd /usr/src/mod_audio_stream; \
    git submodule update --init --recursive; \
    mkdir -p build; \
    cd build; \
    cmake -DCMAKE_BUILD_TYPE=Release ..; \
    make -j"$(nproc)"; \
    make install; \
    ldconfig; \
    rm -rf /usr/src/mod_audio_stream

# --- Add dialplan (9000) and enable module autoload ---
COPY dialplan/ai_voicebot_9000.xml /etc/freeswitch/dialplan/default/ai_voicebot_9000.xml
COPY docker/entrypoint.sh /usr/local/bin/entrypoint.sh

RUN set -eux; \
    chmod +x /usr/local/bin/entrypoint.sh; \
    # Ensure mod_audio_stream is autoloaded
    if ! grep -q 'mod_audio_stream' /etc/freeswitch/autoload_configs/modules.conf.xml; then \
      sed -i 's#</modules>#  <load module="mod_audio_stream"/>\n</modules>#' /etc/freeswitch/autoload_configs/modules.conf.xml; \
    fi

EXPOSE 5060/udp 5060/tcp 5080/udp 5080/tcp 8021/tcp 16384-32768/udp

STOPSIGNAL SIGTERM

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["freeswitch","-nf"]
