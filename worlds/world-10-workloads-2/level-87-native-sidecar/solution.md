# Solution

```yaml
spec:
  initContainers:
  - name: log-shipper
    image: busybox:1.36
    restartPolicy: Always
    command: ["sh", "-c", "tail -F /var/log/app/app.log"]
    volumeMounts:
    - name: logs
      mountPath: /var/log/app
```

```bash
k get pod app -n sidecar-lab -o yaml > app.yaml   # add the block above
k replace --force -f app.yaml
k logs app -n sidecar-lab -c log-shipper
```
