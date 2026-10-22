# Solution

```bash
k autoscale deploy api -n hpa-multi --min=2 --max=6 --cpu=60% $do > hpa.yaml
```

```yaml
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 60
  - type: Resource
    resource:
      name: memory
      target:
        type: AverageValue
        averageValue: 50Mi
```

```bash
k apply -f hpa.yaml
k describe hpa api -n hpa-multi
```
