#!/bin/bash
# Installs project deps into .venv (the system Python's setuptools can't build outscraper).
set -euo pipefail
cd "${CLAUDE_PROJECT_DIR:-$(pwd)}"
[ -x .venv/bin/python ] || python3 -m venv .venv
.venv/bin/pip install -q -r requirements.txt
if [ -n "${CLAUDE_ENV_FILE:-}" ]; then
  echo "export PATH=\"$PWD/.venv/bin:\$PATH\"" >> "$CLAUDE_ENV_FILE"
fi
