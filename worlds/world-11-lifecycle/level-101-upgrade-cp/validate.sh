#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
C="--context $CQ_LAB_CONTEXT"
CP="$(cq_node_name lab-controlplane)"
check "kubeadm is v1.37.1" node_ok lab-controlplane 'kubeadm version -o short | grep -qx v1.37.1'
check 2 "kube-apiserver runs v1.37.1" out_match "v1.37.1" kubectl $C -n kube-system get pod "kube-apiserver-$CP" -o jsonpath='{.spec.containers[0].image}'
check 2 "kubelet on lab-controlplane is v1.37.1" out_eq v1.37.1 kubectl $C get node "$CP" -o jsonpath='{.status.nodeInfo.kubeletVersion}'
check "lab-controlplane is Ready and schedulable" out_eq "True " sh -c "kubectl $C get node $CP -o jsonpath='{.status.conditions[?(@.type==\"Ready\")].status} {.spec.unschedulable}'"
check "lab-node01 was not upgraded" out_match "v1.36" kubectl $C get node "$(cq_node_name lab-node01)" -o jsonpath='{.status.nodeInfo.kubeletVersion}'
finish
