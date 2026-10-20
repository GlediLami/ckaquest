#!/usr/bin/env bash
source "$CQ_ROOT/lib/common.sh"
cq_node_sh controlplane "sed -i 's|- kube-schedular$|- kube-scheduler|' /etc/kubernetes/manifests/kube-scheduler.yaml"
