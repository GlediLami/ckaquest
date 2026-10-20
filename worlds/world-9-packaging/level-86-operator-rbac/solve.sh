#!/usr/bin/env bash
source "$CQ_ROOT/lib/common.sh"
cat <<'EOF' | kubectl apply -f -
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: backup-operator
rules:
- apiGroups: ["ops.example.com"]
  resources: ["backups", "backups/status"]
  verbs: ["get", "list", "watch", "update", "patch"]
EOF
kubectl create clusterrolebinding backup-operator --clusterrole=backup-operator --serviceaccount=backup-system:backup-operator
sleep 12
