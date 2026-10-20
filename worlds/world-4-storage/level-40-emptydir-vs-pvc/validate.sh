#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
uses_pvc() { jp ckaquest pod/data-app "{.spec.volumes[*].persistentVolumeClaim.claimName}" | grep -qw app-data; }
no_emptydir() { [ -z "$(jp ckaquest pod/data-app "{.spec.volumes[*].emptyDir}")" ]; }
check "PVC app-data is Bound" field_eq ckaquest pvc/app-data "{.status.phase}" Bound
check 2 "data-app mounts app-data" uses_pvc
check "no emptyDir left" no_emptydir
check "data-app is Ready" pod_ready ckaquest data-app
finish
