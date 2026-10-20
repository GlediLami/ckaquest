# Solution

```yaml
# overlays/prod/kustomization.yaml
resources:
- ../../base
namespace: kustomize-patch
patches:
- path: limits.yaml
configMapGenerator:
- name: web-config
  literals:
  - MODE=production
```

```yaml
# overlays/prod/limits.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
spec:
  template:
    spec:
      containers:
      - name: web
        resources:
          limits: {memory: 128Mi, cpu: 200m}
        envFrom:
        - configMapRef: {name: web-config}
```
