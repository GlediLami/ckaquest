#!/usr/bin/env bash
source "$CQ_ROOT/lib/common.sh"
kubectl delete priorityclass high-priority batch-low team-standard team-critical --ignore-not-found >/dev/null 2>&1
true
