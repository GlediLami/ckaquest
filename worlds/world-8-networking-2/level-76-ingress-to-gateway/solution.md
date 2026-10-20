# Solution

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: app-route
  namespace: migrate-lab
spec:
  parentRefs:
  - name: web-gw
  hostnames: ["app.example.com"]
  rules:
  - matches:
    - path: {type: PathPrefix, value: /api}
    backendRefs:
    - name: api
      port: 80
  - matches:
    - path: {type: PathPrefix, value: /}
    backendRefs:
    - name: web
      port: 80
```

```bash
k apply -f route.yaml
k delete ingress legacy -n migrate-lab
```
