#!/usr/bin/env bash
# Build the sandbox dir for the "first Dockerfile" lab.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"
SANDBOX="$REPO_ROOT/craft/docker/_sandbox/01-first-image"

rm -rf "$SANDBOX"
mkdir -p "$SANDBOX"

cat > "$SANDBOX/app.py" <<'PY'
"""A tiny app that proves the container works."""

import json
import sys

import requests  # has to be installed via pip

print(json.dumps({
    "python": sys.version.split()[0],
    "msg": "Hello from a container.",
    "requests_version": requests.__version__,
}, indent=2))
PY

cat > "$SANDBOX/requirements.txt" <<'TXT'
requests==2.32.3
TXT

cat <<EOF

✓ Sandbox built at: $SANDBOX

Try:
  cd "$SANDBOX"
  python3 app.py   # confirm the script works (you may need to pip install requests)

Then write Dockerfile and:
  docker build -t lab01 .
  docker run --rm lab01

EOF
