#!/usr/bin/env bash
set -uo pipefail
source "$CQ_ROOT/lib/common.sh"
cert() { openssl req -x509 -newkey rsa:2048 -nodes -days 365 -subj "/CN=$2" -addext "subjectAltName=DNS:$2" -keyout "$1/tls.key" -out "$1/tls.crt" >/dev/null 2>&1; }
T="$(mktemp -d "$CQ_HOME/tls-XXXX")"; cert "$T" web.tls-lab
kubectl create secret tls web-tls -n tls-lab --cert="$T/tls.crt" --key="$T/tls.key" >/dev/null
mv "$T" "$CQ_HOME/backup/tls-121-$(date +%s)"
cat <<'EOF' | kubectl apply -f - >/dev/null
apiVersion: v1
kind: ConfigMap
metadata:
  name: nginx-tls
  namespace: tls-lab
data:
  default.conf: |
    server {
      listen 443 ssl;
      server_name web.tls-lab;
      ssl_certificate     /etc/nginx/tls/tls.crt;
      ssl_certificate_key /etc/nginx/tls/tls.key;
      ssl_protocols TLSv1.3;
      location / { return 200 "tls ok\n"; }
    }
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
  namespace: tls-lab
spec:
  replicas: 1
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
      - name: nginx
        image: nginx:1.27
        ports:
        - containerPort: 443
        volumeMounts:
        - name: conf
          mountPath: /etc/nginx/conf.d/default.conf
          subPath: default.conf
        - name: tls
          mountPath: /etc/nginx/tls
          readOnly: true
      volumes:
      - name: conf
        configMap:
          name: nginx-tls
      - name: tls
        secret:
          secretName: web-tls
---
apiVersion: v1
kind: Service
metadata:
  name: web
  namespace: tls-lab
spec:
  selector:
    app: web
  ports:
  - port: 443
    targetPort: 443
EOF
kubectl rollout status deploy/web -n tls-lab --timeout=120s >/dev/null 2>&1 || true
