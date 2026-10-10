#!/usr/bin/env bash
# Build a sandbox repo with a feature branch diverged from an updated main.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"
SANDBOX="$REPO_ROOT/craft/git/_sandbox/01-rebase-basics"

rm -rf "$SANDBOX"
mkdir -p "$SANDBOX"
cd "$SANDBOX"

git init -q -b main
git config user.email "lab@softtrain.local"
git config user.name "Lab User"

# --- shared base ---
echo "line one" > notes.md
git add notes.md
git commit -q -m "init: notes"

echo "shared base" >> notes.md
git add notes.md
git commit -q -m "shared base"

# --- feature branch from here ---
git switch -q -c feature

echo "feat A" >> notes.md
git add notes.md
git commit -q -m "feat: A"

echo "feat B" >> notes.md
git add notes.md
git commit -q -m "feat: B"

echo "feat C" >> notes.md
git add notes.md
git commit -q -m "feat: C"

# --- main moves forward independently ---
git switch -q main

echo "main update 1" > unrelated.md
git add unrelated.md
git commit -q -m "main: unrelated update 1"

echo "main update 2" >> unrelated.md
git add unrelated.md
git commit -q -m "main: unrelated update 2"

# Leave the user on `feature` so they can see "you are 3 commits ahead, 2 commits behind".
git switch -q feature

cat <<EOF

✓ Sandbox built at: $SANDBOX

Try:
  cd "$SANDBOX"
  git log --oneline --all --graph

Goal: rebase feature onto main, then fast-forward main to feature.

EOF
