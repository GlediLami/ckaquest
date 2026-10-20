#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
writes() { kubectl exec -n ckaquest writer-app -- sh -c "touch /data/.cq-check && rm /data/.cq-check"; }
check "writer-app does not run as root" field_ne ckaquest pod/writer-app "{.spec.securityContext.runAsUser}{.spec.containers[0].securityContext.runAsUser}" 0
check "pod securityContext sets fsGroup" field_ne ckaquest pod/writer-app "{.spec.securityContext.fsGroup}" ""
check "writer-app is Running" pod_running ckaquest writer-app
check 2 "the container can write to /data" writes
finish
