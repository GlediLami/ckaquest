#!/usr/bin/env bash
# Start the CKAQuest game. Your kubectl work happens in a second terminal (source env.sh there).
set -euo pipefail
cd "$(dirname "$0")"
source lib/common.sh

if [ ! -x venv/bin/python3 ]; then
  echo "❌ No Python environment found. Run ./install.sh first."
  exit 1
fi
if [ ! -f "$KUBECONFIG" ]; then
  echo "❌ No CKAQuest cluster yet ($KUBECONFIG missing). Run ./install.sh first."
  exit 1
fi

export PYTHONPATH="$(pwd):${PYTHONPATH:-}"
exec venv/bin/python3 engine/engine.py
