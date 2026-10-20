#!/usr/bin/env bash
source "$CQ_ROOT/lib/common.sh"
cq_restore_manifest kube-scheduler
cq_wait 120 bash -c "kubectl -n kube-system get pod kube-scheduler-ckaquest-control-plane -o jsonpath='{.status.containerStatuses[0].ready}' | grep -q true" || true
