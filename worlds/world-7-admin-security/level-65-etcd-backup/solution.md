# Solution

```bash
ssh controlplane
grep -E 'listen-client|cert-file|key-file|trusted-ca' /etc/kubernetes/manifests/etcd.yaml
etcdctl --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key \
  snapshot save /opt/course/65/etcd-snapshot.db
etcdutl snapshot status /opt/course/65/etcd-snapshot.db -w table > /opt/course/65/status.txt
```
