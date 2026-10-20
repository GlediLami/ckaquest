# Solution

```bash
ssh controlplane
etcdutl snapshot restore /opt/course/66/etcd-backup.db --data-dir /var/lib/etcd-restore
vim /etc/kubernetes/manifests/etcd.yaml
#   volumes:
#   - hostPath:
#       path: /var/lib/etcd-restore     # was /var/lib/etcd
#     name: etcd-data
watch crictl ps                         # etcd and kube-apiserver restart
exit
k get cm ledger -n payments
```
