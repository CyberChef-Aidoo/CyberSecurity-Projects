#!/usr/bin/env bash
set -euo pipefail

echo "== http-headers-scanner setup =="

if ! command -v python3 >/dev/null 2>&1; then
    echo "ERROR: python3 not found. Install Python 3.10+ first."
    exit 1
fi

echo "-> python found: $(python3 --version)"

echo "-> installing dependencies (requests, rich, pytest)"
pip install requests rich pytest --user

echo "-> running tests to confirm everything works"
python3 -m pytest test_http_headers_scanner.py -v

echo ""
echo "Setup complete. Try:"
echo "  python3 http_headers_scanner.py https://example.com"
