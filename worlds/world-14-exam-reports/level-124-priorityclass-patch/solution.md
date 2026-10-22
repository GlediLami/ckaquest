# Solution

```bash
k get priorityclass --sort-by=.value
k create priorityclass high-priority --value=749999
k patch deploy busybox-logger -n priority-lab \
  -p '{"spec":{"template":{"spec":{"priorityClassName":"high-priority"}}}}'
k get pod -n priority-lab -o jsonpath='{.items[*].spec.priority}'
```
