#!/usr/bin/env bash
set -uo pipefail
source "$CQ_ROOT/lib/common.sh"
cat <<'EOF' | kubectl apply -f - >/dev/null
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: backups.ops.example.com
spec:
  group: ops.example.com
  scope: Namespaced
  names:
    plural: backups
    singular: backup
    kind: Backup
    shortNames: [bk]
  versions:
  - name: v1
    served: true
    storage: true
    schema:
      openAPIV3Schema:
        type: object
        properties:
          spec:
            type: object
            required: [schedule, target]
            properties:
              schedule: {type: string}
              target: {type: string}
              retain: {type: integer, minimum: 1}
EOF
kubectl delete clusterrole backup-operator --ignore-not-found >/dev/null
kubectl delete clusterrolebinding backup-operator --ignore-not-found >/dev/null
kubectl create serviceaccount backup-operator -n backup-system >/dev/null
cat <<'EOF' | kubectl apply -f - >/dev/null
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backup-operator
  namespace: backup-system
spec:
  replicas: 1
  selector:
    matchLabels: {app: backup-operator}
  template:
    metadata:
      labels: {app: backup-operator}
    spec:
      serviceAccountName: backup-operator
      containers:
      - name: operator
        image: bitnami/kubectl:latest
        command: ["sh", "-c", "while true; do kubectl get backups.ops.example.com -A 2>&1 | tail -1; sleep 5; done"]
EOF
