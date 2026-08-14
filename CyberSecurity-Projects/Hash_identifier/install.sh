#!/usr/bin/env bash
set -euo pipefail

echo "== hash-identifier setup =="

if ! command -v python3 >/dev/null 2>&1; then
    echo "ERROR: python3 not found. Install Python 3.10+ first."
    exit 1
fi

echo "-> python found: $(python3 --version)"

# echo "-> installing dependencies (rich, pytest)"
# pip install rich pytest --userw

# echo "-> running tests to confirm everything works"
# python3 -m pytest test_hash_identifier.py -v

echo ""
echo "Setup complete. Try:"
echo "  python3 hash_identifier.py 5f4dcc3b5aa765d61d8327deb882cf99"
