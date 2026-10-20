#!/usr/bin/env bash
set -uo pipefail
source "$CQ_ROOT/lib/common.sh"
kubectl create serviceaccount report-sa -n reports >/dev/null
kubectl create configmap report-settings -n reports --from-literal=format=pdf >/dev/null
cat <<'EOF' | kubectl apply -f - >/dev/null
apiVersion: apps/v1
kind: Deployment
metadata:
  name: report-gen
  namespace: reports
spec:
  replicas: 1
  selector:
    matchLabels: {app: report-gen}
  template:
    metadata:
      labels: {app: report-gen}
    spec:
      serviceAccountName: report-sa
      containers:
      - name: gen
        image: bitnami/kubectl:latest
        command: ["sh", "-c", "while true; do kubectl get configmaps -n reports -o name 2>&1 | tail -2; sleep 5; done"]
EOF
