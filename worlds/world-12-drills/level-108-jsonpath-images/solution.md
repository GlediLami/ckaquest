# Solution

```bash
k get pods -n drill-108 -l app=shop \
  -o jsonpath='{range .items[*]}{.metadata.name} {.spec.containers[?(@.name=="sidecar")].image}{"\n"}{end}' \
  > ~/ckaquest-work/108/sidecars.txt
```
