# Solution

```bash
cat ~/ckaquest-work/128/webapp/values.yaml
helm install monitoring-stack ~/ckaquest-work/128/webapp -n monitoring --create-namespace \
  --set replicaCount=3 --set service.type=NodePort
helm list -n monitoring
k get pods,svc -n monitoring
```
