#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
SA=system:serviceaccount:ckaquest:pod-reader
check "Role pod-reader-role exists" exists ckaquest role/pod-reader-role
check 2 "pod-reader can list pods in ckaquest" can_i "$SA" list pods ckaquest
check "pod-reader can watch pods in ckaquest" can_i "$SA" watch pods ckaquest
check "pod-reader cannot delete pods" cannot_i "$SA" delete pods ckaquest
check "pod-reader cannot read secrets" cannot_i "$SA" get secrets ckaquest
check "pod-reader cannot list pods in other namespaces" cannot_i "$SA" list pods kube-system
finish
