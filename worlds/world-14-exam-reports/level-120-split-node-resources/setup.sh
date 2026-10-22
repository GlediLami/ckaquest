#!/usr/bin/env bash
set -uo pipefail
source "$CQ_ROOT/lib/common.sh"
cat <<EOF | kubectl apply -f - >/dev/null
apiVersion: apps/v1
kind: Deployment
metadata:
  name: wordpress
  namespace: resource-lab
spec:
  replicas: 1
  selector:
    matchLabels:
      app: wordpress
  template:
    metadata:
      labels:
        app: wordpress
    spec:
      nodeSelector:
        kubernetes.io/hostname: $(cq_node_name node01)
      initContainers:
      - name: init-db
        image: busybox:1.36
        command: ["sh", "-c", "sleep 2"]
      containers:
      - name: wordpress
        image: busybox:1.36
        command: ["sh", "-c", "sleep 3600"]
EOF
kubectl rollout status deploy/wordpress -n resource-lab --timeout=120s >/dev/null 2>&1 || true
