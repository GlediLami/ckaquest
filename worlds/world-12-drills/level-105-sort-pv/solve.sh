#!/usr/bin/env bash
source "$CQ_ROOT/lib/common.sh"
kubectl get pv --sort-by=.spec.capacity.storage -o jsonpath='{range .items[*]}{.metadata.name}{"\n"}{end}' | grep '^drill-pv-' > "$CQ_WORK/105/pvs.txt"
