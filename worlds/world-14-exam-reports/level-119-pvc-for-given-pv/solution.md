# Solution

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: mariadb
  namespace: mariadb
spec:
  accessModes: ["ReadWriteOnce"]
  storageClassName: mariadb-storage
  volumeName: mariadb-pv
  resources:
    requests:
      storage: 250Mi
```

```bash
k get pv mariadb-pv
k apply -f pvc.yaml
k get pvc -n mariadb                  # Bound
vi ~/ckaquest-work/119/mariadb-deploy.yaml   # claimName: mariadb
k apply -f ~/ckaquest-work/119/mariadb-deploy.yaml
```
