#!/usr/bin/env bash
source "$CQ_ROOT/lib/common.sh"
cq_node_sh node02 "sed -i 's|clientCAFile: .*|clientCAFile: /etc/kubernetes/pki/ca.crt|' /var/lib/kubelet/config.yaml && systemctl restart kubelet"
