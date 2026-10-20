# Solution

```yaml
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
```

```bash
k apply -f route.yaml
k describe httproute shop-route -n shop     # Accepted: True, ResolvedRefs: True
```
