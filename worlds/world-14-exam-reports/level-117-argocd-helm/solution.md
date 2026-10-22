# Solution

```bash
helm repo add argo https://argoproj.github.io/argo-helm     # offline: http://127.0.0.1:8879
helm repo update
helm show values argo/argo-cd --version 10.10.3 | grep -A3 '^crds'
helm template argocd argo/argo-cd --version 10.10.3 -n argocd \
  --set crds.install=false > ~/ckaquest-work/117/argocd.yaml
helm install argocd argo/argo-cd --version 10.10.3 -n argocd --set crds.install=false
helm list -n argocd
```
