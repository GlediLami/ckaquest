#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
L='{.spec.limits[?(@.type=="Container")]'
R='{.spec.containers[0].resources'
too_big() { ! kubectl run cq-big -n team-ns --image=nginx:1.27-alpine --dry-run=server --overrides='{"spec":{"containers":[{"name":"cq-big","image":"nginx:1.27-alpine","resources":{"limits":{"cpu":"1"}}}]}}' >/dev/null 2>&1; }
check "defaultRequest 100m / 64Mi" out_eq "100m 64Mi" kubectl get limits container-defaults -n team-ns -o jsonpath="$L.defaultRequest.cpu} $L.defaultRequest.memory}"
check "default limit 200m / 128Mi" out_eq "200m 128Mi" kubectl get limits container-defaults -n team-ns -o jsonpath="$L.default.cpu} $L.default.memory}"
check "max 500m / 256Mi" out_eq "500m 256Mi" kubectl get limits container-defaults -n team-ns -o jsonpath="$L.max.cpu} $L.max.memory}"
check 2 "pod plain got the defaults" out_eq "100m 200m 64Mi 128Mi" kubectl get pod plain -n team-ns -o jsonpath="$R.requests.cpu} $R.limits.cpu} $R.requests.memory} $R.limits.memory}"
check "a pod asking for 1 CPU is rejected" too_big
finish
