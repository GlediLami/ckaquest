#!/usr/bin/env bash
set -euo pipefail
source "$CQ_ROOT/lib/common.sh"
kubectl uncordon ckaquest-worker2 >/dev/null 2>&1 || true
cat <<YAML | kubectl apply -f - >/dev/null
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
  namespace: $NAMESPACE
spec:
  replicas: 2
  selector:
    matchLabels: {app: web}
  template:
    metadata:
      labels: {app: web}
    spec:
      affinity:
        nodeAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            preference:
              matchExpressions:
              - {key: kubernetes.io/hostname, operator: In, values: [ckaquest-worker2]}
      containers:
      - name: nginx
        image: nginx:1.27-alpine
---
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: web-pdb
  namespace: $NAMESPACE
spec:
  minAvailable: 2
  selector:
    matchLabels: {app: web}
---
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: log-agent
  namespace: $NAMESPACE
spec:
  selector:
    matchLabels: {app: log-agent}
  template:
    metadata:
      labels: {app: log-agent}
    spec:
      containers:
      - name: agent
        image: busybox:1.36
        command: ["sleep", "86400"]
---
apiVersion: v1
kind: Pod
metadata:
  name: debug-shell
  namespace: $NAMESPACE
spec:
  nodeName: ckaquest-worker2
  containers:
  - name: shell
    image: busybox:1.36
    command: ["sleep", "86400"]
YAML
kubectl -n "$NAMESPACE" rollout status deploy/web --timeout=120s >/dev/null
kubectl -n "$NAMESPACE" rollout status deploy/web --timeout=120s >/dev/null
