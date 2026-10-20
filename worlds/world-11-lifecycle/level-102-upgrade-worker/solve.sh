#!/usr/bin/env bash
source "$CQ_ROOT/lib/common.sh"
C="--context $CQ_LAB_CONTEXT"
W="$(cq_node_name lab-node01)"
kubectl $C drain "$W" --ignore-daemonsets --delete-emptydir-data
cq_node_sh lab-node01 "apt-get install -y -qq 'kubeadm=1.37.1-*' >/dev/null && kubeadm upgrade node >/dev/null
apt-get install -y -qq 'kubelet=1.37.1-*' 'kubectl=1.37.1-*' >/dev/null
systemctl daemon-reload && systemctl restart kubelet"
sleep 20
kubectl $C uncordon "$W"
