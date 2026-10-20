#!/usr/bin/env bash
set -uo pipefail
source "$CQ_ROOT/lib/common.sh"
cat <<'EOF' | kubectl apply -f - >/dev/null
apiVersion: apps/v1
kind: Deployment
metadata:
  name: docs
  namespace: ingress-lab
spec:
  replicas: 1
  selector:
    matchLabels: {app: docs}
  template:
    metadata:
      labels: {app: docs}
    spec:
      containers:
      - name: echo
        image: hashicorp/http-echo:1.0
        args: ["-text=docs site", "-listen=:8080"]
        ports:
        - containerPort: 8080
---
apiVersion: v1
kind: Service
metadata:
  name: docs
  namespace: ingress-lab
spec:
  selector: {app: docs}
  ports:
  - port: 80
    targetPort: 8080
EOF
kubectl create ingress docs-ingress -n ingress-lab --rule="docs.example.com/*=docs:80" >/dev/null
