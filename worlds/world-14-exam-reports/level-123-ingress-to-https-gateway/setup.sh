#!/usr/bin/env bash
set -uo pipefail
source "$CQ_ROOT/lib/common.sh"
cert() { openssl req -x509 -newkey rsa:2048 -nodes -days 365 -subj "/CN=$2" -addext "subjectAltName=DNS:$2" -keyout "$1/tls.key" -out "$1/tls.crt" >/dev/null 2>&1; }
T="$(mktemp -d "$CQ_HOME/tls-XXXX")"; cert "$T" shop.example.com
kubectl create secret tls shop-tls -n shop-migrate --cert="$T/tls.crt" --key="$T/tls.key" >/dev/null
mv "$T" "$CQ_HOME/backup/tls-123-$(date +%s)"
kubectl create deployment api -n shop-migrate --image=hashicorp/http-echo:1.0 -- /http-echo -text="shop api" -listen=:5678 >/dev/null
kubectl expose deployment api -n shop-migrate --port=80 --target-port=5678 >/dev/null
kubectl create deployment web -n shop-migrate --image=hashicorp/http-echo:1.0 -- /http-echo -text="shop web" -listen=:5678 >/dev/null
kubectl expose deployment web -n shop-migrate --port=80 --target-port=5678 >/dev/null
cat <<'EOF' | kubectl apply -f - >/dev/null
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: shop
  namespace: shop-migrate
spec:
  ingressClassName: nginx
  tls:
  - hosts: ["shop.example.com"]
    secretName: shop-tls
  rules:
  - host: shop.example.com
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: api
            port:
              number: 80
      - path: /
        pathType: Prefix
        backend:
          service:
            name: web
            port:
              number: 80
EOF
