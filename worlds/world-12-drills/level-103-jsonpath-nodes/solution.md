# Solution

```bash
k get nodes -o jsonpath='{range .items[*]}{.metadata.name} {.status.addresses[?(@.type=="InternalIP")].address}{"\n"}{end}' > ~/ckaquest-work/103/nodes.txt
```
