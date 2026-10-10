#!/usr/bin/env bash
# Build a sandbox repo with a messy feature branch that needs history cleanup.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"
SANDBOX="$REPO_ROOT/craft/git/_sandbox/02-interactive-rebase"

rm -rf "$SANDBOX"
mkdir -p "$SANDBOX"
cd "$SANDBOX"

git init -q -b main
git config user.email "lab@softtrain.local"
git config user.name "Lab User"

# --- main baseline ---
echo "# Project notes" > notes.md
git add notes.md
git commit -q -m "init: project notes"

# --- feature branch with messy history ---
git switch -q -c feature

echo "## Authentication" >> notes.md
git add notes.md
git commit -q -m "add auth section"

echo "basic password flow" >> notes.md
git add notes.md
git commit -q -m "wip"

echo "token refresh logic" >> notes.md
git add notes.md
git commit -q -m "more auth stuff"

echo "## Authorisation" >> notes.md
git add notes.md
git commit -q -m "add authz section (typo fix incoming)"

# simulate a typo fix as a separate commit
sed -i 's/Authorisation/Authorization/' notes.md
git add notes.md
git commit -q -m "fix typo in header"

echo "role-based access rules" >> notes.md
git add notes.md
git commit -q -m "rbac notes"

echo "## TODO: revisit token expiry" >> notes.md
git add notes.md
git commit -q -m "temp: reminder note, remove before merge"

cat <<EOF

✓ Sandbox built at: $SANDBOX

Try:
  cd "$SANDBOX"
  git log --oneline --all --graph

Goal: clean up the feature branch history into 3 tidy commits before merging to main.

EOF
