# Solution

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: monitoring
aggregationRule:
  clusterRoleSelectors:
  - matchLabels:
      rbac.ckaquest.io/aggregate-to-monitoring: "true"
rules: []
```

```bash
k apply -f monitoring.yaml
k create clusterrole monitoring-pods --verb=get,list,watch --resource=pods
k create clusterrole monitoring-nodes --verb=get,list --resource=nodes
k label clusterrole monitoring-pods monitoring-nodes rbac.ckaquest.io/aggregate-to-monitoring=true
k create clusterrolebinding monitoring --clusterrole=monitoring --serviceaccount=agg-lab:monitor
k get clusterrole monitoring -o yaml        # rules are filled in
k auth can-i list nodes --as=system:serviceaccount:agg-lab:monitor
```
