#!/usr/bin/env bash
source "$CQ_ROOT/lib/common.sh"
cq_node_sh node01 'rm -f /etc/kubelet.d/miner.yaml'
for i in $(seq 1 30); do kubectl get pod crypto-miner-ckaquest-worker -n default >/dev/null 2>&1 || break; sleep 3; done
