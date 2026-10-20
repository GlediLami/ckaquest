#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
check 2 "shared-pvc is ReadWriteMany" field_eq access-mode pvc/shared-pvc "{.spec.accessModes[0]}" ReadWriteMany
check "shared-pvc is Bound to shared-storage" field_eq access-mode pvc/shared-pvc "{.spec.volumeName}" shared-storage
check 2 "web-servers has 3/3 ready replicas" deploy_ready access-mode web-servers 3
finish
