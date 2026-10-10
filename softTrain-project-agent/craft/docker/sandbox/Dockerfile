# Sandbox image — used by tools/sandbox.sh to run risky commands in isolation.
# Includes bash + git + jq + standard GNU coreutils + python + node.

FROM debian:bookworm-slim

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        bash \
        ca-certificates \
        curl \
        less \
        nano \
        git \
        jq \
        gawk \
        sed \
        grep \
        findutils \
        coreutils \
        python3 \
        python3-pip \
        nodejs \
        ripgrep \
        tree \
        bsdmainutils \
    && rm -rf /var/lib/apt/lists/*

# Safe defaults: the sandbox should refuse to do anything *outside* /work
# without explicit intent. Set HOME and a non-prompting shell.
ENV HOME=/tmp/sandbox-home \
    PS1='\\[\\e[33m\\][sandbox]\\[\\e[0m\\] \\w\\$ '

WORKDIR /work

# Default entrypoint: bash. The wrapper script can override the command.
CMD ["bash"]
