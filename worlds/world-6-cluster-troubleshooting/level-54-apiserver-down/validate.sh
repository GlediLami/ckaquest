#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
check 2 "API server answers" cq_api_up
check "apiserver talks to etcd on the client port 2379" node_ok controlplane 'grep -q -- "--etcd-servers=https://127.0.0.1:2379" /etc/kubernetes/manifests/kube-apiserver.yaml'
check "kube-apiserver pod is Ready" pod_ready kube-system kube-apiserver-ckaquest-control-plane
check "all nodes Ready" all_nodes_ready
finish
