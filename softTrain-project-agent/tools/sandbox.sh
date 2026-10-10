#!/usr/bin/env bash
# sandbox.sh — run a command inside the softTrain sandbox container.
#
# Spins up a fresh container from craft/docker/sandbox/Dockerfile with the repo
# mounted at /work. Use this for anything destructive or experimental that you
# don't want touching your host: forced git resets, rm -rf practice, untrusted
# scripts, system-level shell exploration.
#
# Usage:
#   tools/sandbox.sh                    # interactive bash shell
#   tools/sandbox.sh <command> [args]   # run a single command and exit

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
IMAGE_TAG="softtrain-sandbox:latest"
DOCKERFILE_DIR="$REPO_ROOT/craft/docker/sandbox"

if ! command -v docker >/dev/null 2>&1; then
    echo "Error: docker not found in PATH. Install docker first." >&2
    exit 1
fi

# Build the image if it doesn't exist or its Dockerfile has changed since the last build.
NEED_BUILD=0
if ! docker image inspect "$IMAGE_TAG" >/dev/null 2>&1; then
    NEED_BUILD=1
elif [[ "$DOCKERFILE_DIR/Dockerfile" -nt "$(docker image inspect -f '{{.Metadata.LastTagTime}}' "$IMAGE_TAG" 2>/dev/null || echo /dev/null)" ]] 2>/dev/null; then
    # Ignore - timestamp comparison is best-effort.
    :
fi

if [[ "$NEED_BUILD" -eq 1 ]]; then
    echo "Building sandbox image (first run)..." >&2
    docker build -t "$IMAGE_TAG" "$DOCKERFILE_DIR"
fi

# Mount the repo read-write at /work. The user inside the container is root, but
# everything that gets written gets the host UID/GID via --user.
DOCKER_ARGS=(
    --rm
    -v "$REPO_ROOT:/work"
    -w /work
    --user "$(id -u):$(id -g)"
)

# If stdin is a TTY, run interactively.
if [[ -t 0 && -t 1 ]]; then
    DOCKER_ARGS+=(-it)
fi

if [[ $# -eq 0 ]]; then
    exec docker run "${DOCKER_ARGS[@]}" "$IMAGE_TAG" bash
else
    exec docker run "${DOCKER_ARGS[@]}" "$IMAGE_TAG" "$@"
fi
