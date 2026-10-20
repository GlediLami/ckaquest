# Solution

```bash
k get pv --sort-by=.spec.capacity.storage -o jsonpath='{range .items[*]}{.metadata.name}{"\n"}{end}' \
  | grep '^drill-pv-' > ~/ckaquest-work/105/pvs.txt
```
