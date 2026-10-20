#!/usr/bin/env bash
source "$CQ_ROOT/lib/common.sh"
cq_node_sh controlplane "sed -i 's|controller-manager.config|controller-manager.conf|' /etc/kubernetes/manifests/kube-controller-manager.yaml"
