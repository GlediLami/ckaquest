#!/usr/bin/env bash
source "$CQ_ROOT/lib/common.sh"
cat <<'EOF' | kubectl apply -f -
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: shop-gw
  namespace: shop-migrate
spec:
  gatewayClassName: nginx
  listeners:
  - name: https
    protocol: HTTPS
    port: 443
    hostname: shop.example.com
    tls:
      mode: Terminate
      certificateRefs:
      - name: shop-tls
---
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: shop-route
  namespace: shop-migrate
spec:
  parentRefs:
  - name: shop-gw
  hostnames: ["shop.example.com"]
  rules:
  - matches:
    - path:
        type: PathPrefix
        value: /api
    backendRefs:
    - name: api
      port: 80
  - matches:
    - path:
        type: PathPrefix
        value: /
    backendRefs:
    - name: web
      port: 80
EOF
kubectl delete ingress shop -n shop-migrate
up() { [ -n "$(kubectl get svc -n shop-migrate -l gateway.networking.k8s.io/gateway-name=shop-gw -o jsonpath='{.items[0].spec.clusterIP}')" ] && kubectl get gateway shop-gw -n shop-migrate -o jsonpath='{.status.conditions[?(@.type=="Programmed")].status}' | grep -q True; }
cq_wait 180 up; sleep 20
