#!/usr/bin/env bash
source "$CQ_ROOT/lib/common.sh"
cat <<'EOF' | kubectl apply -f -
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: monitoring
aggregationRule:
  clusterRoleSelectors:
  - matchLabels:
      rbac.ckaquest.io/aggregate-to-monitoring: "true"
rules: []
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: monitoring-pods
  labels:
    rbac.ckaquest.io/aggregate-to-monitoring: "true"
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list", "watch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: monitoring-nodes
  labels:
    rbac.ckaquest.io/aggregate-to-monitoring: "true"
rules:
- apiGroups: [""]
  resources: ["nodes"]
  verbs: ["get", "list"]
EOF
kubectl create clusterrolebinding monitoring --clusterrole=monitoring --serviceaccount=agg-lab:monitor
sleep 3
