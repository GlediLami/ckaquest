# Solution

```bash
k autoscale deploy api -n hpa-lab --min=2 --max=6 --cpu-percent=60 $do > hpa.yaml
```

```yaml
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Pods
        value: 1
        periodSeconds: 60
```

```bash
k apply -f hpa.yaml
k describe hpa api -n hpa-lab
```
