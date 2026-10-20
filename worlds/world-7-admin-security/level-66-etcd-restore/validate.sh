#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
check 2 "etcd runs from /var/lib/etcd-restore" node_ok controlplane 'grep -q "path: /var/lib/etcd-restore" /etc/kubernetes/manifests/etcd.yaml'
check "API server answers" cq_api_up
check 3 "ConfigMap ledger is back" field_eq payments cm/ledger '{.data.balance}' 1000000
check "all nodes Ready" all_nodes_ready
finish
