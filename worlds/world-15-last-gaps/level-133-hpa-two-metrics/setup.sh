#!/usr/bin/env bash
set -uo pipefail
source "$CQ_ROOT/lib/common.sh"
cat <<'EOF' | kubectl apply -f - >/dev/null
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
  namespace: hpa-multi
spec:
  replicas: 1
  selector:
    matchLabels:
      app: api
  template:
    metadata:
      labels:
        app: api
    spec:
      containers:
      - name: api
        image: nginx:1.27
        resources:
          requests:
            cpu: 100m
            memory: 64Mi
EOF
kubectl rollout status deploy/api -n hpa-multi --timeout=120s >/dev/null 2>&1 || true
