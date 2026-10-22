#!/usr/bin/env bash
source "$CQ_ROOT/lib/common.sh"
top=$(kubectl get priorityclass -o jsonpath='{range .items[*]}{.metadata.name} {.value}{"\n"}{end}' | grep -v '^system-' | awk '{print $2}' | sort -n | tail -1)
kubectl create priorityclass high-priority --value=$((top - 1))
kubectl patch deploy busybox-logger -n priority-lab -p '{"spec":{"template":{"spec":{"priorityClassName":"high-priority"}}}}'
kubectl rollout status deploy/busybox-logger -n priority-lab --timeout=120s
gone() { [ "$(kubectl get pods -n priority-lab -l app=busybox-logger --no-headers | wc -l)" = 1 ]; }
cq_wait 60 gone
