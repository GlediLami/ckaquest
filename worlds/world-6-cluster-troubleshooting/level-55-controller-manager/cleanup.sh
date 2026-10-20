#!/usr/bin/env bash
source "$CQ_ROOT/lib/common.sh"
cq_restore_manifest kube-controller-manager
cq_wait 120 bash -c "kubectl -n kube-system get pod kube-controller-manager-ckaquest-control-plane -o jsonpath='{.status.containerStatuses[0].ready}' | grep -q true" || true
