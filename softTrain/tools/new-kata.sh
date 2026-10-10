#!/usr/bin/env bash
# new-kata.sh — stub a new kata file from the template.
#
# Usage: tools/new-kata.sh <python|typescript> <topic> <name>
#
# Example: tools/new-kata.sh python strings palindrome

set -euo pipefail

if [[ $# -ne 3 ]]; then
    echo "Usage: $0 <python|typescript> <topic> <name>" >&2
    exit 2
fi

LANG="$1"
TOPIC="$2"
NAME="$3"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

case "$LANG" in
    python) EXT="py"; COMMENT="#" ;;
    typescript) EXT="ts"; COMMENT="//" ;;
    *) echo "Error: <lang> must be 'python' or 'typescript'" >&2; exit 1 ;;
esac

PROMPT_DIR="$REPO_ROOT/kata/$LANG/$TOPIC"
SOLUTION_DIR="$REPO_ROOT/kata/$LANG/_solutions/$TOPIC"
PROMPT_FILE="$PROMPT_DIR/$NAME.$EXT"
SOLUTION_FILE="$SOLUTION_DIR/$NAME.$EXT"

if [[ -e "$PROMPT_FILE" ]]; then
    echo "Error: $PROMPT_FILE already exists" >&2
    exit 1
fi

mkdir -p "$PROMPT_DIR" "$SOLUTION_DIR"

if [[ "$LANG" == "python" ]]; then
    cat > "$PROMPT_FILE" <<'EOF'
"""
TODO: Problem statement.

Examples:
    >>> example_function(...)
    expected_output
"""


def solve(...):
    raise NotImplementedError


# --- tests ---
import pytest


def test_solve_basic():
    assert solve(...) == ...


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
EOF
    cat > "$SOLUTION_FILE" <<'EOF'
"""Reference solution. See kata prompt file for the problem statement."""


def solve(...):
    raise NotImplementedError  # TODO: write the canonical solution
EOF
else
    cat > "$PROMPT_FILE" <<'EOF'
/**
 * TODO: Problem statement.
 *
 * @example
 *   solve(...) // -> expected
 */
export function solve(/* args */): unknown {
    throw new Error("Not implemented");
}

if (import.meta.vitest) {
    const { test, expect } = import.meta.vitest;
    test("basic case", () => {
        expect(solve(/* ... */)).toBe(/* ... */);
    });
}
EOF
    cat > "$SOLUTION_FILE" <<'EOF'
// Reference solution. See kata prompt file for the problem statement.
export function solve(/* args */): unknown {
    throw new Error("Not implemented");
}
EOF
fi

echo "✓ Created $PROMPT_FILE"
echo "✓ Created $SOLUTION_FILE"
echo ""
echo "Open the prompt, fill in the problem, then drill it."
