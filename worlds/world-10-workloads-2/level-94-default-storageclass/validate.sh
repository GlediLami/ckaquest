#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
A='{.metadata.annotations.storageclass\.kubernetes\.io/is-default-class}'
defaults() { kubectl get sc -o jsonpath='{range .items[*]}{.metadata.name}={.metadata.annotations.storageclass\.kubernetes\.io/is-default-class}{"\n"}{end}' | grep -c '=true$'; }
check "local-retain: local-path, Retain, WaitForFirstConsumer" out_eq "rancher.io/local-path Retain WaitForFirstConsumer" kubectl get sc local-retain -o jsonpath='{.provisioner} {.reclaimPolicy} {.volumeBindingMode}'
check 2 "local-retain is the default" field_eq - sc/local-retain "$A" true
check "exactly one default StorageClass" out_eq 1 defaults
check "PVC data has no class in the manifest but got local-retain" field_eq sc-lab pvc/data '{.spec.storageClassName}' local-retain
check 2 "PVC data is Bound" field_eq sc-lab pvc/data '{.status.phase}' Bound
check "pod user is Ready" pod_ready sc-lab user
finish
