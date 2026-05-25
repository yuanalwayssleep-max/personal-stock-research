#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"
if [ ! -d .venv ]; then
  /Users/cocoon/.local/bin/python3.11 -m venv .venv
fi
source .venv/bin/activate
pip install -e .
streamlit run app.py \
  --server.address 0.0.0.0 \
  --server.port 8501 \
  --server.headless true \
  --server.enableCORS false \
  --server.enableXsrfProtection false
