#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
check 2 "app-storage-claim is Bound" field_eq ckaquest pvc/app-storage-claim "{.status.phase}" Bound
check "it is bound to PV app-storage" field_eq ckaquest pvc/app-storage-claim "{.spec.volumeName}" app-storage
check 2 "database-pod is Ready" pod_ready ckaquest database-pod
finish
