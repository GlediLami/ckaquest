# Solution

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: local-wffc
provisioner: kubernetes.io/no-provisioner
volumeBindingMode: WaitForFirstConsumer
---
apiVersion: v1
kind: PersistentVolume
metadata:
  name: wffc-pv
spec:
  capacity: {storage: 200Mi}
  accessModes: ["ReadWriteOnce"]
  storageClassName: local-wffc
  local:
    path: /mnt/wffc
  nodeAffinity:
    required:
      nodeSelectorTerms:
      - matchExpressions:
        - {key: kubernetes.io/hostname, operator: In, values: [<node02 name>]}
```

```bash
k apply -f storage.yaml
k apply -f pvc.yaml; k get pvc -n wffc-lab        # Pending
k apply -f pod.yaml;  k get pvc -n wffc-lab        # Bound
```
