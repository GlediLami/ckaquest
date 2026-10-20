# Solution

```yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: container-defaults
  namespace: team-ns
spec:
  limits:
  - type: Container
    defaultRequest: {cpu: 100m, memory: 64Mi}
    default: {cpu: 200m, memory: 128Mi}
    max: {cpu: 500m, memory: 256Mi}
```

```bash
k run plain -n team-ns --image=nginx:1.27-alpine
k get pod plain -n team-ns -o jsonpath='{.spec.containers[0].resources}'
```
