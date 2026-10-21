#!/usr/bin/env bash
# Level 46: node01 is a dedicated GPU node. node02 stays free, so other tasks keep a place to run.
set -euo pipefail
source "$CQ_ROOT/lib/common.sh"
kubectl taint node "$(cq_node_name node01)" dedicated=gpu:NoSchedule --overwrite >/dev/null
echo "node01 is tainted dedicated=gpu:NoSchedule"
