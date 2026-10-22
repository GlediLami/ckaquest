#!/usr/bin/env bash
set -uo pipefail
source "$CQ_ROOT/lib/common.sh"
cat <<'EOF' | kubectl apply -f - >/dev/null
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-logger
  namespace: logs-lab
spec:
  replicas: 1
  selector:
    matchLabels:
      app: app-logger
  template:
    metadata:
      labels:
        app: app-logger
    spec:
      containers:
      - name: app
        image: busybox:1.36
        command: ["sh", "-c", "i=0; while true; do i=$((i+1)); echo \"$(date) request $i done\" >> /var/log/app.log; sleep 2; done"]
EOF
kubectl rollout status deploy/app-logger -n logs-lab --timeout=120s >/dev/null 2>&1 || true
