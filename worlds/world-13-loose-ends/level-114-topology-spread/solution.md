# Solution

```bash
k label node node01 topology.kubernetes.io/zone=zone-a     # use the real node names
k label node node02 topology.kubernetes.io/zone=zone-b
k edit deploy api -n spread-lab
```

```yaml
spec:
  template:
    spec:
      topologySpreadConstraints:
      - maxSkew: 1
        topologyKey: topology.kubernetes.io/zone
        whenUnsatisfiable: DoNotSchedule
        labelSelector:
          matchLabels:
            app: api
        matchLabelKeys:
        - pod-template-hash
```

```bash
k get pods -n spread-lab -o wide        # 2 per node
```
