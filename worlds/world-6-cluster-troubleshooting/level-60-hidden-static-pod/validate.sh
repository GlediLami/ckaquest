#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
no_miner() { ! kubectl get pods -n default --no-headers 2>/dev/null | grep -q '^crypto-miner'; }
check 2 "no crypto-miner pod in default" no_miner
check 2 "the manifest is gone from the static pod path on node01" node_ok node01 '! grep -rl "crypto-miner" /etc/kubelet.d /etc/kubernetes/manifests 2>/dev/null | grep -q .'
check "kubelet keeps its staticPodPath (not reconfigured)" node_ok node01 'grep -q "staticPodPath: /etc/kubelet.d" /var/lib/kubelet/config.yaml'
check "node01 is Ready" node_ready ckaquest-worker
finish
