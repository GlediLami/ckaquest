#!/usr/bin/env bash
set -uo pipefail
source "$CQ_ROOT/lib/common.sh"
cat <<'EOF' | kubectl apply -f - >/dev/null
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-v1
  namespace: api-split
spec:
  replicas: 1
  selector:
    matchLabels: {app: api-v1}
  template:
    metadata:
      labels: {app: api-v1}
    spec:
      containers:
      - name: echo
        image: hashicorp/http-echo:1.0
        args: ["-text=api v1", "-listen=:8080"]
        ports:
        - containerPort: 8080
---
apiVersion: v1
kind: Service
metadata:
  name: api-v1
  namespace: api-split
spec:
  selector: {app: api-v1}
  ports:
  - port: 80
    targetPort: 8080
EOF
cat <<'EOF' | kubectl apply -f - >/dev/null
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-v2
  namespace: api-split
spec:
  replicas: 1
  selector:
    matchLabels: {app: api-v2}
  template:
    metadata:
      labels: {app: api-v2}
    spec:
      containers:
      - name: echo
        image: hashicorp/http-echo:1.0
        args: ["-text=api v2", "-listen=:8080"]
        ports:
        - containerPort: 8080
---
apiVersion: v1
kind: Service
metadata:
  name: api-v2
  namespace: api-split
spec:
  selector: {app: api-v2}
  ports:
  - port: 80
    targetPort: 8080
EOF
cat <<'EOF' | kubectl apply -f - >/dev/null
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: web-gw
  namespace: api-split
spec:
  gatewayClassName: nginx
  listeners:
  - name: http
    protocol: HTTP
    port: 80
EOF
cq_wait 120 bash -c '[ -n "$(kubectl get svc -n api-split -l gateway.networking.k8s.io/gateway-name=web-gw -o name)" ]'
