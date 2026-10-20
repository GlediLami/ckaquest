#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
own_claims() {
  local i tpl; tpl="$(jp statefulset-volumes sts/postgres-cluster "{.spec.volumeClaimTemplates[0].metadata.name}")"
  [ -n "$tpl" ] || return 1
  for i in 0 1 2; do field_eq statefulset-volumes "pvc/$tpl-postgres-cluster-$i" "{.status.phase}" Bound || return 1; done
}
sts_ready() { [ "$(jp statefulset-volumes sts/postgres-cluster "{.status.readyReplicas}")" = 3 ]; }
check "postgres-cluster has a volumeClaimTemplate" field_ne statefulset-volumes sts/postgres-cluster "{.spec.volumeClaimTemplates[0].metadata.name}" ""
check 2 "each replica has its own Bound PVC" own_claims
check "the shared PVC database-storage is gone" not_exists statefulset-volumes pvc/database-storage
check 2 "3/3 replicas are ready" sts_ready
finish
