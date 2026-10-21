# Solution

```bash
k patch sc slow-local -p '{"allowVolumeExpansion": true}'
k patch pvc data -n grow-lab -p '{"spec":{"resources":{"requests":{"storage":"2Gi"}}}}'
k get pvc data -n grow-lab
```
