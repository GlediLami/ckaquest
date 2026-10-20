#!/usr/bin/env bash
set -uo pipefail
source "$CQ_ROOT/lib/common.sh"
cq_node_backup controlplane /root/.kube/config
cq_node_sh controlplane "sed -i -e 's|:6443|:6444|' -e 's|^current-context: .*|current-context: kubernetes-admin@kubernetez|' /root/.kube/config"
