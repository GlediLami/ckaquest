#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
check "app-storage uses an existing StorageClass" exists - "sc/$(jp storageclass pvc/app-storage "{.spec.storageClassName}")"
check 2 "app-storage is Bound" field_eq storageclass pvc/app-storage "{.status.phase}" Bound
check 2 "data-processor is Ready" pod_ready storageclass data-processor
finish
