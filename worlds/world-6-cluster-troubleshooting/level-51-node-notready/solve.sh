#!/usr/bin/env bash
source "$CQ_ROOT/lib/common.sh"
cq_node_sh node01 'systemctl enable --now kubelet'
