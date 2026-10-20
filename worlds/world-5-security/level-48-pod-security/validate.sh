#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
P=pod/secure-app
nonroot() { [ "$(jp pss-lab $P '{.spec.securityContext.runAsNonRoot}')" = true ] || [ "$(jp pss-lab $P '{.spec.containers[0].securityContext.runAsNonRoot}')" = true ]; }
seccomp() { jp pss-lab $P '{.spec.securityContext.seccompProfile.type}{.spec.containers[0].securityContext.seccompProfile.type}' | grep -Eq 'RuntimeDefault|Localhost'; }
check "namespace still enforces restricted" field_eq - ns/pss-lab '{.metadata.labels.pod-security\.kubernetes\.io/enforce}' restricted
check "image unchanged (busybox:1.36)" field_eq pss-lab $P '{.spec.containers[0].image}' busybox:1.36
check "runAsNonRoot is true" nonroot
check "allowPrivilegeEscalation is false" field_eq pss-lab $P '{.spec.containers[0].securityContext.allowPrivilegeEscalation}' false
check "all capabilities dropped" field_match pss-lab $P '{.spec.containers[0].securityContext.capabilities.drop}' 'ALL'
check "seccomp profile RuntimeDefault (or Localhost)" seccomp
check 2 "secure-app is Running" pod_running pss-lab secure-app
finish
