#!/usr/bin/env bash
source "$CQ_ROOT/lib/common.sh"
cat <<'EOF' | kubectl apply -f -
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: shop-route
  namespace: shop
spec:
  parentRefs:
  - name: web-gw
  hostnames: ["shop.example.com"]
  rules:
  - backendRefs:
    - name: shop-frontend
      port: 80
EOF
