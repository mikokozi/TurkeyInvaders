#!/usr/bin/env bash
set -euo pipefail

# Turkey Invaders launcher using a local .venv
# Usage:
#   ./start.sh               # run normally (curses)
#   ./start.sh --headless    # run headless (non-TTY), CI smoke
#   ./start.sh --headless 1  # headless for 1 second

here() { cd "$(dirname "${BASH_SOURCE[0]}")" && pwd; }
PROJ_DIR="$(here)"
cd "$PROJ_DIR"

# Ensure python3 is available
if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 not found. Please install Python 3.10+" >&2
  exit 1
fi

# Create venv if missing
if [ ! -d .venv ]; then
  echo "Creating virtual environment in .venv" >&2
  python3 -m venv .venv
fi

# Activate venv
source .venv/bin/activate

# Optional: install dependencies if requirements.txt is present
if [ -f requirements.txt ]; then
  python -m pip install --upgrade pip >/dev/null 2>&1 || true
  pip install -r requirements.txt
fi

# Reset terminal on exit (in case curses crashes)
trap 'stty sane >/dev/null 2>&1 || true' EXIT

# Parse optional headless flag
if [ "${1-}" = "--headless" ]; then
  export TI_HEADLESS=1
  if [ -n "${2-}" ]; then export TI_HEADLESS_SECONDS="$2"; fi
fi

exec python -m turkey_invaders

