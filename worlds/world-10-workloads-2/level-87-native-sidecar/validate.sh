#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
I='{.spec.initContainers[?(@.name=="log-shipper")]'
ships() { kubectl logs app -n sidecar-lab -c log-shipper --tail=3 2>/dev/null | grep -q "order processed"; }
check 2 "log-shipper is an init container with restartPolicy Always" field_eq sidecar-lab pod/app "$I.restartPolicy}" Always
check "it mounts the logs volume" field_eq sidecar-lab pod/app "$I.volumeMounts[0].name}" logs
check "pod app is Ready" pod_ready sidecar-lab app
check 2 "log-shipper prints the app log" ships
finish
