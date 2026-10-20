#!/usr/bin/env bash
set -euo pipefail
source "$CQ_ROOT/lib/common.sh"
kubectl label namespace "$NAMESPACE" --overwrite \
  pod-security.kubernetes.io/enforce=restricted \
  pod-security.kubernetes.io/warn=restricted >/dev/null
mkdir -p "$CQ_WORK/48"
cat > "$CQ_WORK/48/secure-app.yaml" <<YAML
apiVersion: v1
kind: Pod
metadata:
  name: secure-app
  namespace: pss-lab
spec:
  containers:
  - name: app
    image: busybox:1.36
    command: ["sh", "-c", "echo running as \$(id -u); sleep 86400"]
    securityContext:
      runAsUser: 0
      allowPrivilegeEscalation: true
YAML
echo "Manifest written to $CQ_WORK/48/secure-app.yaml"
