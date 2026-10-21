#!/usr/bin/env bash
set -uo pipefail
source "$CQ_ROOT/lib/common.sh"
for n in node01 node02; do kubectl label node "$(cq_node_name $n)" topology.kubernetes.io/zone- >/dev/null 2>&1; done
cat <<EOF | kubectl apply -f - >/dev/null
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
  namespace: spread-lab
spec:
  replicas: 4
  selector:
    matchLabels:
      app: api
  template:
    metadata:
      labels:
        app: api
    spec:
      affinity:
        nodeAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            preference:
              matchExpressions:
              - key: kubernetes.io/hostname
                operator: In
                values: ["$(cq_node_name node01)"]
      containers:
      - name: api
        image: nginx:1.27
EOF
kubectl rollout status deploy/api -n spread-lab --timeout=120s >/dev/null 2>&1 || true
