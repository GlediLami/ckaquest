#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
reads() { kubectl exec -n ckaquest web-app -- cat /app/config/app.conf | grep -q app_name; }
check "the volume is mounted at /app/config" field_eq ckaquest pod/web-app "{.spec.containers[0].volumeMounts[0].mountPath}" /app/config
check "web-app is Running" pod_running ckaquest web-app
check 2 "/app/config/app.conf exists in the pod" reads
finish
