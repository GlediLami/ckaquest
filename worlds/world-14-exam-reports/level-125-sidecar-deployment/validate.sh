#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
C='{.spec.template.spec.containers'
mount() { kubectl get deploy app-logger -n logs-lab -o jsonpath="$C[?(@.name==\"$1\")].volumeMounts[?(@.name==\"logs\")].mountPath}"; }
sidecar_cmd() { kubectl get deploy app-logger -n logs-lab -o jsonpath="$C[?(@.name==\"sidecar\")].command}$C[?(@.name==\"sidecar\")].args}"; }
reads() { kubectl logs deploy/app-logger -n logs-lab -c sidecar --tail=5 2>/dev/null | grep -q "request"; }
check "volume logs is an emptyDir" out_eq '{}' kubectl get deploy app-logger -n logs-lab -o jsonpath='{.spec.template.spec.volumes[?(@.name=="logs")].emptyDir}'
check "app mounts logs at /var/log" out_eq /var/log mount app
check "sidecar mounts logs at /var/log" out_eq /var/log mount sidecar
check "sidecar runs tail -f on /var/log/app.log" out_match 'tail.*-[fF].*/var/log/app.log|tail.*/var/log/app.log.*-[fF]' sidecar_cmd
check "Deployment is Ready" deploy_ready logs-lab app-logger
check 3 "kubectl logs -c sidecar shows the app's lines" reads
finish
