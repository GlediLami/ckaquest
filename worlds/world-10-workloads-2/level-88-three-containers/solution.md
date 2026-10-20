# Solution

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: trio
  namespace: trio-lab
spec:
  volumes:
  - name: shared
    emptyDir: {}
  containers:
  - name: writer
    image: busybox:1.36
    command: ["sh", "-c", "while true; do date >> /data/dates; sleep 5; done"]
    volumeMounts: [{name: shared, mountPath: /data}]
  - name: reader
    image: busybox:1.36
    command: ["sh", "-c", "tail -F /data/dates"]
    volumeMounts: [{name: shared, mountPath: /data}]
  - name: info
    image: busybox:1.36
    command: ["sleep", "3600"]
    env:
    - name: MY_NODE
      valueFrom:
        fieldRef: {fieldPath: spec.nodeName}
```
