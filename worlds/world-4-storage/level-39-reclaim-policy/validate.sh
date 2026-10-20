#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
check 2 "important-data has reclaim policy Retain" field_eq - pv/important-data "{.spec.persistentVolumeReclaimPolicy}" Retain
check "data-claim is still Bound" field_eq reclaim-policy pvc/data-claim "{.status.phase}" Bound
check "data-writer is Running" pod_running reclaim-policy data-writer
finish
