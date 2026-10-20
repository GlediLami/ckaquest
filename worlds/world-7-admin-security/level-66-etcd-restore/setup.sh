#!/usr/bin/env bash
set -uo pipefail
source "$CQ_ROOT/lib/common.sh"
kubectl create configmap ledger -n payments --from-literal=balance=1000000 >/dev/null
cq_node_backup controlplane /etc/kubernetes/manifests/etcd.yaml
cq_node_sh controlplane 'mkdir -p /opt/course/66 /root/.cq-trash
[ -d /var/lib/etcd-restore ] && mv /var/lib/etcd-restore /root/.cq-trash/etcd-restore-$(date +%s)
mv -f /opt/course/66/etcd-backup.db /root/.cq-trash/ 2>/dev/null || true
etcdctl --endpoints=https://127.0.0.1:2379 --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt --key=/etc/kubernetes/pki/etcd/server.key \
  snapshot save /opt/course/66/etcd-backup.db >/dev/null 2>&1'
kubectl delete configmap ledger -n payments >/dev/null
