#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
SA=system:serviceaccount:rbac-permission:pod-reader
check "Role pod-reader-role exists" exists rbac-permission role/pod-reader-role
check 2 "pod-reader can list pods in rbac-permission" can_i "$SA" list pods rbac-permission
check "pod-reader can watch pods in rbac-permission" can_i "$SA" watch pods rbac-permission
check "pod-reader cannot delete pods" cannot_i "$SA" delete pods rbac-permission
check "pod-reader cannot read secrets" cannot_i "$SA" get secrets rbac-permission
check "pod-reader cannot list pods in other namespaces" cannot_i "$SA" list pods kube-system
finish
