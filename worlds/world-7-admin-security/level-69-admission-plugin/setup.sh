#!/usr/bin/env bash
set -uo pipefail
source "$CQ_ROOT/lib/common.sh"
cq_node_backup controlplane /etc/kubernetes/manifests/kube-apiserver.yaml
kubectl delete namespace auto-created --ignore-not-found --timeout=90s >/dev/null
