#!/usr/bin/env bash
set -euo pipefail
source "$CQ_ROOT/lib/common.sh"
kubectl -n kube-system patch ds kube-proxy --type=json \
  -p '[{"op":"replace","path":"/spec/template/spec/containers/0/command/1","value":"--config=/var/lib/kube-proxy/kube-proxy.conf"}]' >/dev/null
# Replace all kube-proxy pods at once (a rolling update would break only one node)
kubectl -n kube-system delete pods -l k8s-app=kube-proxy --wait=false >/dev/null
sleep 5
cq_wait 120 bash -c "[ \"\$(kubectl -n kube-system get ds kube-proxy -o jsonpath='{.status.numberReady}')\" = 0 ]"
kubectl create deployment echo -n "$NAMESPACE" --image=nginx:1.27-alpine --replicas=2 >/dev/null
kubectl expose deployment echo -n "$NAMESPACE" --port=80 >/dev/null
