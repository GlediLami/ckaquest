#!/usr/bin/env bash
set -euo pipefail
source "$CQ_ROOT/lib/common.sh"
mkdir -p "$CQ_WORK/58"
rm -f "$CQ_WORK/58/cpu-hog.txt" "$CQ_WORK/58/busy-node.txt"
pod() {  # pod <name> <cpu-request> <cpu-limit> <command>
cat <<YAML | kubectl apply -f - >/dev/null
apiVersion: v1
kind: Pod
metadata:
  name: $1
  namespace: $NAMESPACE
spec:
  containers:
  - name: worker
    image: busybox:1.36
    command: ["sh", "-c", "$4"]
    resources:
      requests:
        cpu: $2
      limits:
        cpu: $3
YAML
}
pod cache-warmer 10m 100m "sleep 86400"
pod session-store 10m 100m "sleep 86400"
pod report-generator 50m 500m "while true; do :; done"
kubectl wait -n "$NAMESPACE" --for=condition=Ready pod --all --timeout=120s >/dev/null
echo "Waiting for metrics (up to 2 minutes)..."
cq_wait 180 bash -c "kubectl top pod -n $NAMESPACE --no-headers | grep -q report-generator"
