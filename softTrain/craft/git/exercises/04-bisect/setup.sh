#!/usr/bin/env bash
# Build a sandbox repo with 12 commits where commit #7 introduces a regression.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"
SANDBOX="$REPO_ROOT/craft/git/_sandbox/04-bisect"

rm -rf "$SANDBOX"
mkdir -p "$SANDBOX"
cd "$SANDBOX"

git init -q -b main
git config user.email "lab@softtrain.local"
git config user.name "Lab User"

# A small Python "feature": double the input.
write_double() {
    local op="$1"
    cat > calc.py <<PY
def calc(x: int) -> int:
    return x ${op} 2

if __name__ == "__main__":
    print(calc(5))
PY
}

write_test() {
    cat > test.sh <<'SH'
#!/usr/bin/env bash
out=$(python3 calc.py 2>/dev/null || true)
expected="10"
if [[ "$out" == "$expected" ]]; then
    exit 0
else
    echo "expected $expected got $out" >&2
    exit 1
fi
SH
    chmod +x test.sh
}

# Helper to add a non-functional commit.
non_func_commit() {
    local msg="$1"
    local file="$2"
    echo "$msg" >> "$file"
    git add "$file"
    git commit -q -m "$msg"
}

# Initial good commit.
write_double "*"
write_test
echo "# Tiny calculator" > README.md
git add .
git commit -q -m "01: init calc + test"

# A few more good commits — readme tweaks, comments — that don't break the test.
non_func_commit "02: add usage notes" README.md
non_func_commit "03: more notes" README.md
non_func_commit "04: typo fix" README.md
non_func_commit "05: tidy" README.md
non_func_commit "06: another readme update" README.md

# THE BUG: commit 07 changes calc to use + instead of *. test.sh now fails.
write_double "+"
git add calc.py
git commit -q -m "07: refactor calc — looks innocent, breaks behaviour"

# A few more commits after the bug.
non_func_commit "08: more notes" README.md
non_func_commit "09: doc tweak" README.md
non_func_commit "10: comment cleanup" README.md
non_func_commit "11: indentation polish" README.md
non_func_commit "12: HEAD" README.md

cat <<EOF

✓ Sandbox built at: $SANDBOX

Confirm the regression:
  cd "$SANDBOX"
  bash test.sh   # should fail
  git checkout HEAD~11 -- calc.py && bash test.sh   # should pass — but you'll need to git restore --staged then git checkout calc.py before bisecting

Goal: use git bisect to find which commit broke test.sh.

EOF
