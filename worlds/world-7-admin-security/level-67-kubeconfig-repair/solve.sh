#!/usr/bin/env bash
source "$CQ_ROOT/lib/common.sh"
cq_node_sh controlplane "sed -i -e 's|:6444|:6443|' -e 's|^current-context: .*|current-context: kubernetes-admin@ckaquest|' /root/.kube/config"
cq_node_sh controlplane 'kubectl config get-contexts -o name | head -1 | xargs kubectl config use-context'
