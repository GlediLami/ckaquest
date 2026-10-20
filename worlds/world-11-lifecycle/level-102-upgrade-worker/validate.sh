#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
C="--context $CQ_LAB_CONTEXT"
W="$(cq_node_name lab-node01)"
check "kubeadm on lab-node01 is v1.37.1" node_ok lab-node01 'kubeadm version -o short | grep -qx v1.37.1'
check 3 "kubelet on lab-node01 is v1.37.1" out_eq v1.37.1 kubectl $C get node "$W" -o jsonpath='{.status.nodeInfo.kubeletVersion}'
check 2 "lab-node01 is Ready and schedulable" out_eq "True " sh -c "kubectl $C get node $W -o jsonpath='{.status.conditions[?(@.type==\"Ready\")].status} {.spec.unschedulable}'"
finish
