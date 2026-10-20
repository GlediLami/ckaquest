#!/usr/bin/env bash
set -uo pipefail
source "$CQ_ROOT/lib/common.sh"
cat <<'EOF' | kubectl apply -f - >/dev/null
apiVersion: apps/v1
kind: Deployment
metadata:
  name: blog
  namespace: blog
spec:
  replicas: 1
  selector:
    matchLabels: {app: blog}
  template:
    metadata:
      labels: {app: blog}
    spec:
      containers:
      - name: echo
        image: hashicorp/http-echo:1.0
        args: ["-text=blog home", "-listen=:8080"]
        ports:
        - containerPort: 8080
---
apiVersion: v1
kind: Service
metadata:
  name: blog
  namespace: blog
spec:
  selector: {app: blog}
  ports:
  - port: 80
    targetPort: 8080
EOF
cat <<'EOF' | kubectl apply -f - >/dev/null
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: web-gw
  namespace: blog
spec:
  gatewayClassName: nginx
  listeners:
  - name: http
    protocol: HTTP
    port: 80
EOF
cq_wait 120 bash -c '[ -n "$(kubectl get svc -n blog -l gateway.networking.k8s.io/gateway-name=web-gw -o name)" ]'
cat <<'EOF' | kubectl apply -f - >/dev/null
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: blog-route
  namespace: blog
spec:
  parentRefs:
  - name: web-gateway
  hostnames: ["blog.example.com"]
  rules:
  - backendRefs:
    - name: blog
      port: 8080
EOF
