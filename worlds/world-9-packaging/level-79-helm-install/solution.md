# Solution

```bash
helm repo add cq http://127.0.0.1:8879
helm search repo cq/webapp --versions
helm show values cq/webapp --version 1.0.0
helm install shop cq/webapp --version 1.0.0 -n helm-shop --set replicaCount=2
helm list -n helm-shop
```
