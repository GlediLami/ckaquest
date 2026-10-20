#!/usr/bin/env bash
set -euo pipefail
source "$CQ_ROOT/lib/common.sh"
cq_break_manifest kube-controller-manager 's|--kubeconfig=/etc/kubernetes/controller-manager.conf|--kubeconfig=/etc/kubernetes/controller-manager.config|'
cq_wait 120 bash -c "! kubectl -n kube-system get pod kube-controller-manager-ckaquest-control-plane -o jsonpath='{.status.containerStatuses[0].ready}' | grep -q true"
sleep 5
kubectl create deployment api -n "$NAMESPACE" --image=nginx:1.27-alpine --replicas=3 >/dev/null
