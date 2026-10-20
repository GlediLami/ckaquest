#!/usr/bin/env bash
source "$CQ_ROOT/lib/common.sh"
cq_node_sh controlplane "sed -i 's|--etcd-servers=https://127.0.0.1:2397|--etcd-servers=https://127.0.0.1:2379|' /etc/kubernetes/manifests/kube-apiserver.yaml"
cq_wait_api 180
