#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
non_ds_pods_on_node2() {
  kubectl get pods -n maint --field-selector spec.nodeName=ckaquest-worker2 \
    -o jsonpath='{range .items[*]}{.metadata.ownerReferences[0].kind}{"\n"}{end}' | grep -v '^DaemonSet$' | grep -q .
}
pdb_protects() {
  local min max
  min="$(jp maint pdb/web-pdb '{.spec.minAvailable}')"; max="$(jp maint pdb/web-pdb '{.spec.maxUnavailable}')"
  { [ -n "$min" ] && [ "$min" -ge 1 ] && [ "$min" -lt 2 ]; } || { [ -n "$max" ] && [ "$max" = 1 ]; }
}
check 2 "node02 is cordoned" field_eq - node/ckaquest-worker2 '{.spec.unschedulable}' true
node2_clear() { ! non_ds_pods_on_node2; }
check 2 "no non-DaemonSet pods of maint left on node02" node2_clear
check "deployment web has 2 ready replicas" deploy_ready maint web 2
check "web-pdb still exists and protects 1 pod" pdb_protects
check "log-agent DaemonSet was not deleted" exists maint ds/log-agent
finish
