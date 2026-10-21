# Solution

```yaml
spec:
  replicas: 3
  template:
    spec:
      affinity:
        podAntiAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
          - labelSelector:
              matchLabels:
                app: cache
            topologyKey: kubernetes.io/hostname
```

```bash
k scale deploy cache -n anti-lab --replicas=0
k edit deploy cache -n anti-lab        # add the block above, replicas 3
k get pods -n anti-lab -o wide         # 2 Running on different nodes, 1 Pending
k describe pod <pending pod> -n anti-lab   # didn't match pod anti-affinity rules
```
