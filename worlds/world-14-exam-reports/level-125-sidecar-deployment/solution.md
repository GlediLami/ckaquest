# Solution

```yaml
spec:
  template:
    spec:
      volumes:
      - name: logs
        emptyDir: {}
      containers:
      - name: app
        # ...unchanged...
        volumeMounts:
        - name: logs
          mountPath: /var/log
      - name: sidecar
        image: busybox:1.36
        command: ["/bin/sh", "-c", "tail -n+1 -f /var/log/app.log"]
        volumeMounts:
        - name: logs
          mountPath: /var/log
```

```bash
k edit deploy app-logger -n logs-lab
k logs deploy/app-logger -n logs-lab -c sidecar
```
