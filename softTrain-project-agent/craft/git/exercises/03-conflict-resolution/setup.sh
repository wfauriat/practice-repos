#!/usr/bin/env bash
# Build a sandbox repo where rebasing feature onto main causes a conflict.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"
SANDBOX="$REPO_ROOT/craft/git/_sandbox/03-conflict-resolution"

rm -rf "$SANDBOX"
mkdir -p "$SANDBOX"
cd "$SANDBOX"

git init -q -b main
git config user.email "lab@softtrain.local"
git config user.name "Lab User"

# --- shared base: a config file both branches will touch ---
cat <<'EOF' > config.md
# Service config

timeout: 30
retries: 3
log_level: info
EOF
git add config.md
git commit -q -m "init: service config"

# --- feature branch: change timeout and add a note ---
git switch -q -c feature

cat <<'EOF' > config.md
# Service config

timeout: 60
retries: 3
log_level: info
EOF
git add config.md
git commit -q -m "feat: increase timeout for slow upstream"

cat <<'EOF' > config.md
# Service config

timeout: 60
retries: 3
log_level: info

# reviewed by: ops team
EOF
git add config.md
git commit -q -m "docs: add review sign-off"

# --- main: someone else also changed timeout (and retries) ---
git switch -q main

cat <<'EOF' > config.md
# Service config

timeout: 10
retries: 5
log_level: info
EOF
git add config.md
git commit -q -m "perf: tighten timeout, increase retries"

# Leave user on feature
git switch -q feature

cat <<EOF

✓ Sandbox built at: $SANDBOX

Try:
  cd "$SANDBOX"
  git log --oneline --all --graph

Goal: rebase feature onto main, resolve the conflict, end with a clean linear history.

EOF
