# Solution

```yaml
# ~/ckaquest-work/83/overlays/prod/kustomization.yaml
resources:
- ../../base
namespace: kustomize-prod
namePrefix: prod-
replicas:
- name: web
  count: 3
images:
- name: nginx
  newTag: 1.28-alpine
```

```bash
k kustomize ~/ckaquest-work/83/overlays/prod
k apply -k ~/ckaquest-work/83/overlays/prod
```
