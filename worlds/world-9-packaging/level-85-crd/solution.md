# Solution

```bash
k apply -f ~/ckaquest-work/85/backup-crd.yaml
k api-resources | grep backups          # SHORTNAMES column: bk
k explain backup.spec
cat <<EOF | k apply -f -
apiVersion: ops.example.com/v1
kind: Backup
metadata:
  name: nightly
  namespace: crd-lab
spec:
  schedule: "0 2 * * *"
  target: postgres
  retain: 7
EOF
echo bk > ~/ckaquest-work/85/shortname.txt
```
