#!/usr/bin/env bash
source "$CQ_ROOT/lib/common.sh"
cq_node_restore controlplane /root/.kube/config
true
