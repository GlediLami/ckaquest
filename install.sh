#!/usr/bin/env bash
# CKAQuest installer for Linux, WSL2 and macOS.
# Creates a Python venv and the dedicated kind cluster. Never touches ~/.kube/config.
set -euo pipefail
cd "$(dirname "$0")"
source lib/common.sh
source cluster/versions.env

echo "🎮 CKAQuest installation"
echo "========================"

missing=0
need() {
  if command -v "$1" >/dev/null; then
    echo "✅ $1"
  else
    echo "❌ $1 not found. $2"
    missing=1
  fi
}
need docker  "Install Docker Desktop (macOS/WSL2) or Docker Engine (Linux)."
need kubectl "brew install kubectl, or https://kubernetes.io/docs/tasks/tools/"
need kind    "brew install kind, or https://kind.sigs.k8s.io/docs/user/quick-start/#installation"
need helm    "brew install helm, or https://helm.sh/docs/intro/install/"
need jq      "brew install jq, or sudo apt install jq"
need openssl "brew install openssl, or sudo apt install openssl"
need python3 "Python 3.9 or newer"
[ "$missing" = 0 ] || exit 1

python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)' || {
  echo "❌ Python 3.9+ required"; exit 1; }

if [ ! -d venv ]; then
  echo "🐍 Creating Python virtual environment..."
  python3 -m venv venv
fi
venv/bin/pip install -q -r requirements.txt
echo "✅ Python packages installed"

bin/cq-cluster up

mkdir -p "$CQ_WORK"
echo
echo "🚀 Setup complete."
echo "   Terminal 1:  ./play.sh"
echo "   Terminal 2:  source $(pwd)/env.sh"
echo "   Exam mode:   ./exam.sh"
