#!/usr/bin/env bash
source "$CQ_ROOT/lib/common.sh"
cq_node_sh controlplane 'kubeadm token create --ttl 2h --print-join-command > /opt/course/70/join.sh'
