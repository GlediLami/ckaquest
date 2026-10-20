#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
check 2 "node ckaquest-worker2 is Ready" node_ready ckaquest-worker2
check "kubelet is running on node02" node_ok node02 'systemctl is-active --quiet kubelet'
check "clientCAFile points to the cluster CA" node_ok node02 'grep -q "clientCAFile: /etc/kubernetes/pki/ca.crt" /var/lib/kubelet/config.yaml'
finish
