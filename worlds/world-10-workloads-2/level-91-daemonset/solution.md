# Solution

```bash
k create deploy node-agent -n agent-lab --image=busybox:1.36 $do -- sleep 3600 > ds.yaml
# kind: DaemonSet, delete replicas/strategy/status, then add:
```

```yaml
    spec:
      tolerations:
      - key: node-role.kubernetes.io/control-plane
        operator: Exists
        effect: NoSchedule
      containers:
      - ...
        resources:
          requests: {cpu: 10m, memory: 16Mi}
```
