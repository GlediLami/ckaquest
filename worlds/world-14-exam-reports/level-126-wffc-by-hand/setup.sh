#!/usr/bin/env bash
set -uo pipefail
source "$CQ_ROOT/lib/common.sh"
kubectl delete pv wffc-pv --ignore-not-found >/dev/null 2>&1
kubectl delete sc local-wffc --ignore-not-found >/dev/null 2>&1
cq_node_sh node02 'mkdir -p /mnt/wffc'
