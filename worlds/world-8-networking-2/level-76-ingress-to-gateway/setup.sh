#!/usr/bin/env bash
set -uo pipefail
source "$CQ_ROOT/lib/common.sh"
cat <<'EOF' | kubectl apply -f - >/dev/null
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
  namespace: migrate-lab
spec:
  replicas: 1
  selector:
    matchLabels: {app: api}
  template:
    metadata:
      labels: {app: api}
    spec:
      containers:
      - name: echo
        image: hashicorp/http-echo:1.0
        args: ["-text=api backend", "-listen=:8080"]
        ports:
        - containerPort: 8080
---
apiVersion: v1
kind: Service
metadata:
  name: api
  namespace: migrate-lab
spec:
  selector: {app: api}
  ports:
  - port: 80
    targetPort: 8080
EOF
cat <<'EOF' | kubectl apply -f - >/dev/null
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
  namespace: migrate-lab
spec:
  replicas: 1
  selector:
    matchLabels: {app: web}
  template:
    metadata:
      labels: {app: web}
    spec:
      containers:
      - name: echo
        image: hashicorp/http-echo:1.0
        args: ["-text=web frontend", "-listen=:8080"]
        ports:
        - containerPort: 8080
---
apiVersion: v1
kind: Service
metadata:
  name: web
  namespace: migrate-lab
spec:
  selector: {app: web}
  ports:
  - port: 80
    targetPort: 8080
EOF
cat <<'EOF' | kubectl apply -f - >/dev/null
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: web-gw
  namespace: migrate-lab
spec:
  gatewayClassName: nginx
  listeners:
  - name: http
    protocol: HTTP
    port: 80
EOF
cq_wait 120 bash -c '[ -n "$(kubectl get svc -n migrate-lab -l gateway.networking.k8s.io/gateway-name=web-gw -o name)" ]'
kubectl create ingress legacy -n migrate-lab --rule="app.example.com/api*=api:80" --rule="app.example.com/*=web:80" >/dev/null
