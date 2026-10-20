#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
K='kubectl --kubeconfig /etc/kubernetes/admin.conf'
W="$(cq_node_name bare-node01)"
check 2 "bare-node01 is a Ready node" node_ok bare-controlplane "$K get node $W --no-headers | grep -q ' Ready'"
check 2 "pod hello runs on bare-node01" node_ok bare-controlplane "[ \"\$($K get pod hello -o jsonpath='{.spec.nodeName} {.status.phase}')\" = '$W Running' ]"
finish
