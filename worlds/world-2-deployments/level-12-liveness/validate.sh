#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
probe_path() { jp liveness deploy/api-server '{.spec.template.spec.containers[0].livenessProbe.httpGet.path}'; }
probe_serves() {
  local pod path
  pod="$(kubectl get pods -n liveness -l app=api --field-selector=status.phase=Running -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)"
  path="$(probe_path)"
  [ -n "$pod" ] && [ -n "$path" ] && kubectl exec -n liveness "$pod" -- wget -q -O /dev/null "http://localhost:80$path" >/dev/null 2>&1
}
no_restarts() {
  local r
  r="$(kubectl get pods -n liveness -l app=api -o jsonpath='{.items[*].status.containerStatuses[*].restartCount}' 2>/dev/null)"
  [ -n "$r" ] && ! tr ' ' '\n' <<<"$r" | grep -qv '^0$'
}
check "api-server still has a liveness probe" field_ne liveness deploy/api-server '{.spec.template.spec.containers[0].livenessProbe.httpGet.port}' ""
check 2 "the probe path returns 200 from nginx" probe_serves
check "api-server has 2/2 ready replicas" deploy_ready liveness api-server 2
check "current pods have not restarted" no_restarts
finish
