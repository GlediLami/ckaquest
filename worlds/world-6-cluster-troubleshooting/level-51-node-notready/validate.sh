#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
check 2 "node ckaquest-worker is Ready" node_ready ckaquest-worker
check "kubelet is running on node01" node_ok node01 'systemctl is-active --quiet kubelet'
check "kubelet starts on boot (enabled)" node_ok node01 'systemctl is-enabled --quiet kubelet'
finish
