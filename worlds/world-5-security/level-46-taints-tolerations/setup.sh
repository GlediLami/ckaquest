#!/usr/bin/env bash
# Level 46: both workers are dedicated GPU nodes. The control plane already has its own taint.
set -euo pipefail
for n in ckaquest-worker ckaquest-worker2; do
  kubectl taint node "$n" dedicated=gpu:NoSchedule --overwrite >/dev/null
done
echo "node01 and node02 are tainted dedicated=gpu:NoSchedule"
