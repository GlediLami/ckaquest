# Solution

```bash
helm template preview webapp --repo http://127.0.0.1:8879 --version 1.1.0 \
  --set replicaCount=3 --set service.type=NodePort > ~/ckaquest-work/82/preview.yaml
```
