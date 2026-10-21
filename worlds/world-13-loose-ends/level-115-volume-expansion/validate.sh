#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
same_uid() { [ -n "$(jp grow-lab cm/original "{.data.$1}")" ] && [ "$(jp grow-lab "$2" '{.metadata.uid}')" = "$(jp grow-lab cm/original "{.data.$1}")" ]; }
check 2 "StorageClass slow-local allows volume expansion" field_eq - sc/slow-local '{.allowVolumeExpansion}' true
check 2 "PVC data requests 2Gi" field_eq grow-lab pvc/data '{.spec.resources.requests.storage}' 2Gi
check "it is the same PVC as before" same_uid pvc pvc/data
check "pod db was not recreated and is Running" same_uid pod pod/db
check "pod db is Running" pod_running grow-lab db
finish
