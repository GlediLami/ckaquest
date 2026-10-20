#!/usr/bin/env bash
source "$CQ_ROOT/lib/common.sh"
cq_node_sh controlplane 'etcdutl snapshot restore /opt/course/66/etcd-backup.db --data-dir /var/lib/etcd-restore
sed -i "s|path: /var/lib/etcd$|path: /var/lib/etcd-restore|" /etc/kubernetes/manifests/etcd.yaml'
sleep 20
cq_wait_api 240
