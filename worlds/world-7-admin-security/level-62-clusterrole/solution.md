# Solution

```bash
k create clusterrole node-reader --verb=get,list,watch --resource=nodes
k create clusterrolebinding node-inspector-binding --clusterrole=node-reader --serviceaccount=monitoring:node-inspector
k auth can-i list nodes --as=system:serviceaccount:monitoring:node-inspector
```
