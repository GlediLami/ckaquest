#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
check "app-storage uses an existing StorageClass" exists - "sc/$(jp ckaquest pvc/app-storage "{.spec.storageClassName}")"
check 2 "app-storage is Bound" field_eq ckaquest pvc/app-storage "{.status.phase}" Bound
check 2 "data-processor is Ready" pod_ready ckaquest data-processor
finish
