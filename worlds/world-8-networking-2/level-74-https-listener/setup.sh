#!/usr/bin/env bash
set -uo pipefail
source "$CQ_ROOT/lib/common.sh"
cat <<'EOF' | kubectl apply -f - >/dev/null
apiVersion: apps/v1
kind: Deployment
metadata:
  name: secure-app
  namespace: secure-shop
spec:
  replicas: 1
  selector:
    matchLabels: {app: secure-app}
  template:
    metadata:
      labels: {app: secure-app}
    spec:
      containers:
      - name: echo
        image: hashicorp/http-echo:1.0
        args: ["-text=secure shop", "-listen=:8080"]
        ports:
        - containerPort: 8080
---
apiVersion: v1
kind: Service
metadata:
  name: secure-app
  namespace: secure-shop
spec:
  selector: {app: secure-app}
  ports:
  - port: 80
    targetPort: 8080
EOF
cat <<'EOF' | kubectl apply -f - >/dev/null
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: web-gw
  namespace: secure-shop
spec:
  gatewayClassName: nginx
  listeners:
  - name: http
    protocol: HTTP
    port: 80
EOF
cq_wait 120 bash -c '[ -n "$(kubectl get svc -n secure-shop -l gateway.networking.k8s.io/gateway-name=web-gw -o name)" ]'
W="$(cq_work_dir 74)"
openssl req -x509 -nodes -newkey rsa:2048 -days 365 -subj "/CN=secure.example.com" \
  -addext "subjectAltName=DNS:secure.example.com" -keyout "$W/tls.key" -out "$W/tls.crt" 2>/dev/null
cat <<'EOF' | kubectl apply -f - >/dev/null
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: secure-route
  namespace: secure-shop
spec:
  parentRefs:
  - name: web-gw
    sectionName: http
  hostnames: ["secure.example.com"]
  rules:
  - backendRefs:
    - name: secure-app
      port: 80
EOF
