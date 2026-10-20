#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
SA=system:serviceaccount:reports:report-sa
works() { kubectl logs deploy/report-gen -n reports --tail=2 2>/dev/null | grep -q "configmap/report-settings"; }
check "Deployment still runs as report-sa" field_eq reports deploy/report-gen '{.spec.template.spec.serviceAccountName}' report-sa
check 2 "report-sa can list configmaps in reports" can_i "$SA" list configmaps reports
check "report-sa cannot read secrets" cannot_i "$SA" get secrets reports
check "report-sa cannot change configmaps" cannot_i "$SA" delete configmaps reports
check 2 "the job now lists configmaps" works
finish
