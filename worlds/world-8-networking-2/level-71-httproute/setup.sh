#!/usr/bin/env bash
set -uo pipefail
source "$CQ_ROOT/lib/common.sh"
cat <<'EOF' | kubectl apply -f - >/dev/null
apiVersion: apps/v1
kind: Deployment
metadata:
  name: shop-frontend
  namespace: shop
spec:
  replicas: 1
  selector:
    matchLabels: {app: shop-frontend}
  template:
    metadata:
      labels: {app: shop-frontend}
    spec:
      containers:
      - name: echo
        image: hashicorp/http-echo:1.0
        args: ["-text=shop frontend", "-listen=:8080"]
        ports:
        - containerPort: 8080
---
apiVersion: v1
kind: Service
metadata:
  name: shop-frontend
  namespace: shop
spec:
  selector: {app: shop-frontend}
  ports:
  - port: 80
    targetPort: 8080
EOF
cat <<'EOF' | kubectl apply -f - >/dev/null
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: web-gw
  namespace: shop
spec:
  gatewayClassName: nginx
  listeners:
  - name: http
    protocol: HTTP
    port: 80
EOF
cq_wait 120 bash -c '[ -n "$(kubectl get svc -n shop -l gateway.networking.k8s.io/gateway-name=web-gw -o name)" ]'
