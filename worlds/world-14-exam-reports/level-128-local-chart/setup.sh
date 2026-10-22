#!/usr/bin/env bash
set -uo pipefail
source "$CQ_ROOT/lib/common.sh"
helm uninstall monitoring-stack -n monitoring >/dev/null 2>&1
kubectl delete ns monitoring --ignore-not-found --wait=true >/dev/null 2>&1
W="$(cq_work_dir 128)"
[ -e "$W/webapp" ] && mv "$W/webapp" "$W/webapp.old.$(date +%s)"
cp -r "$CQ_ROOT/charts/webapp" "$W/webapp"
