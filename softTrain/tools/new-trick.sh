#!/usr/bin/env bash
# new-trick.sh — append a dated entry to craft/tricks/<YYYY-MM>.md.
#
# Usage: tools/new-trick.sh "<one-line description of the trick>"

set -euo pipefail

if [[ $# -lt 1 ]]; then
    echo "Usage: $0 \"<trick description>\"" >&2
    exit 2
fi

TRICK="$*"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MONTH=$(date +%Y-%m)
TODAY=$(date +%Y-%m-%d)
FILE="$REPO_ROOT/craft/tricks/$MONTH.md"

# Create the monthly file with a header if it doesn't exist.
if [[ ! -f "$FILE" ]]; then
    mkdir -p "$(dirname "$FILE")"
    cat > "$FILE" <<EOF
# Tricks — $(date +'%B %Y')

A dated journal of small wins. Each entry: 1-3 lines on the trick, why it matters,
where you encountered it.

EOF
fi

# Append. Ensure a blank line separates entries.
{
    echo ""
    echo "## $TODAY"
    echo ""
    echo "- $TRICK"
} >> "$FILE"

echo "✓ Appended to $FILE"
