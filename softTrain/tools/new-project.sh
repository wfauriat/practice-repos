#!/usr/bin/env bash
# new-project.sh — stub a new mini-project from the template.
#
# Usage: tools/new-project.sh <project-name>

set -euo pipefail

if [[ $# -ne 1 ]]; then
    echo "Usage: $0 <project-name>" >&2
    exit 2
fi

NAME="$1"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DIR="$REPO_ROOT/projects/$NAME"

if [[ -e "$DIR" ]]; then
    echo "Error: $DIR already exists" >&2
    exit 1
fi

mkdir -p "$DIR"
TODAY=$(date +%Y-%m-%d)

cat > "$DIR/README.md" <<EOF
# $NAME

Started: $TODAY

## Goal

<!-- One sentence: what does "done" look like? -->

## Learning aims

<!-- The actual reason you're doing this. The product is secondary. -->

- [ ]
- [ ]

## Stretch goals

<!-- Things you'd love to add if time permits. Don't let stretches block "done". -->

- [ ]

## Working notes

<!-- Append-only log. What did you try? What surprised you? What did you give up on? -->

### $TODAY

## Retrospective

<!-- Fill this in when you ship (or abandon) the project. -->

- **What went well:**
- **What was harder than expected:**
- **What would you keep / change next time:**
- **Did the learning aims actually land?**
EOF

echo "✓ Created $DIR/README.md"
echo ""
echo "Edit the goal + learning aims, then start hacking."
