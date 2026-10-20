# Solution

```bash
k create clusterrole backup-operator --verb=get,list,watch,update,patch \
  --resource=backups.ops.example.com,backups.ops.example.com/status
k create clusterrolebinding backup-operator --clusterrole=backup-operator \
  --serviceaccount=backup-system:backup-operator
k auth can-i list backups.ops.example.com -A --as=system:serviceaccount:backup-system:backup-operator
```
