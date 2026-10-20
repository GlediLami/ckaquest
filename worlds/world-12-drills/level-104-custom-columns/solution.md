# Solution

```bash
k get pods -n drill-104 --sort-by=.metadata.name \
  -o custom-columns=POD:.metadata.name,IMAGE:.spec.containers[0].image,NODE:.spec.nodeName > ~/ckaquest-work/104/pods.txt
```
