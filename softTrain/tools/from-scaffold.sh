#!/usr/bin/env bash
# from-scaffold.sh — copy a scaffold to a new location and prep it for use.
#
# Usage: tools/from-scaffold.sh <scaffold-name> <target-dir>
#
# Example: tools/from-scaffold.sh python-fastapi-crud ~/code/my-new-api

set -euo pipefail

if [[ $# -ne 2 ]]; then
    echo "Usage: $0 <scaffold-name> <target-dir>" >&2
    echo "" >&2
    echo "Available scaffolds:" >&2
    REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
    if [[ -d "$REPO_ROOT/scaffolds" ]]; then
        find "$REPO_ROOT/scaffolds" -mindepth 1 -maxdepth 1 -type d -printf '  - %f\n' >&2
    fi
    exit 2
fi

SCAFFOLD="$1"
TARGET="$2"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SOURCE="$REPO_ROOT/scaffolds/$SCAFFOLD"

if [[ ! -d "$SOURCE" ]]; then
    echo "Error: scaffold '$SCAFFOLD' not found at $SOURCE" >&2
    exit 1
fi

if [[ -e "$TARGET" ]]; then
    echo "Error: target '$TARGET' already exists; refusing to overwrite" >&2
    exit 1
fi

# Resolve target to absolute, then copy.
mkdir -p "$(dirname "$TARGET")"
cp -r "$SOURCE" "$TARGET"
TARGET_ABS="$(cd "$TARGET" && pwd)"
NEW_NAME="$(basename "$TARGET_ABS")"

# Best-effort name swap. Don't fail the whole script if the file is missing.
if [[ -f "$TARGET_ABS/pyproject.toml" ]]; then
    sed -i "s/name = \"$SCAFFOLD\"/name = \"$NEW_NAME\"/" "$TARGET_ABS/pyproject.toml" || true
fi
if [[ -f "$TARGET_ABS/package.json" ]]; then
    sed -i "s/\"name\": \"$SCAFFOLD\"/\"name\": \"$NEW_NAME\"/" "$TARGET_ABS/package.json" || true
fi

# Drop any stale lockfile-installs (.venv, node_modules) — these belong to the source scaffold.
rm -rf "$TARGET_ABS/.venv" "$TARGET_ABS/node_modules"

# Re-init git fresh in the new project (you don't want softTrain's history).
(cd "$TARGET_ABS" && rm -rf .git && git init -q && git add -A && git commit -q -m "Initial commit from scaffold: $SCAFFOLD" 2>/dev/null) || true

cat <<EOF
✓ Scaffold '$SCAFFOLD' → $TARGET_ABS
  Project name set to '$NEW_NAME'.

Next steps:
  cd "$TARGET_ABS"
  cat README.md            # scaffold-specific setup notes
  just --list              # see canonical commands (if 'just' is installed)
EOF
