#!/usr/bin/env bash
# Level 45: label one worker as the GPU node. broken.yaml is applied by the engine afterwards.
set -euo pipefail
kubectl label node ckaquest-worker accelerator=gpu --overwrite >/dev/null
echo "node01 (ckaquest-worker) is labeled accelerator=gpu"
