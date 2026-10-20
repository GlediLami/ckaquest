# Solution

```bash
k config set-context --current --namespace=drill-106
k run web --image=nginx:1.27-alpine -l tier=web
k create deploy api --image=nginx:1.27-alpine --replicas=3
k expose deploy api --port=80
k create cm cfg --from-literal=mode=fast
k create secret generic token --from-literal=t=abc123
k create sa bot
k create role pod-reader --verb=get,list --resource=pods
k create rolebinding bot-pod-reader --role=pod-reader --serviceaccount=drill-106:bot
k config set-context --current --namespace=default
```
