#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
C="{.spec.containers[0].securityContext"
uid() { [ "$(jp ckaquest pod/web-app "$C.runAsUser}")" = 1000 ] || [ "$(jp ckaquest pod/web-app "{.spec.securityContext.runAsUser}")" = 1000 ]; }
nonroot() { jp ckaquest pod/web-app "$C.runAsNonRoot} {.spec.securityContext.runAsNonRoot}" | grep -qw true; }
check "runs as UID 1000" uid
check "runAsNonRoot is true" nonroot
check "allowPrivilegeEscalation is false" field_eq ckaquest pod/web-app "$C.allowPrivilegeEscalation}" false
check 2 "web-app is Ready" pod_ready ckaquest web-app
check "the process really runs as 1000" out_eq 1000 kubectl exec -n ckaquest web-app -- id -u
finish
