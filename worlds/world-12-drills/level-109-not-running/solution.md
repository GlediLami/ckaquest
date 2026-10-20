# Solution

```bash
k get pods -A --field-selector=status.phase!=Running,status.phase!=Succeeded \
  -o jsonpath='{range .items[*]}{.metadata.namespace}/{.metadata.name}{"\n"}{end}' \
  | grep -v '^kube-system/' > ~/ckaquest-work/109/broken.txt
```
