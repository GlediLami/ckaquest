# Solution

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: local-retain
  annotations:
    storageclass.kubernetes.io/is-default-class: "true"
provisioner: rancher.io/local-path
reclaimPolicy: Retain
volumeBindingMode: WaitForFirstConsumer
```

```bash
k annotate sc standard storageclass.kubernetes.io/is-default-class=false --overwrite
k get sc          # only local-retain shows (default)
```
