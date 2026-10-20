#!/usr/bin/env bash
source "$CQ_ROOT/lib/common.sh"
"$CQ_ROOT/cluster/stages.sh" bare joined
W="$(cq_node_name bare-node01)"
cq_node_sh bare-controlplane "kubectl --kubeconfig /etc/kubernetes/admin.conf run hello --image=nginx:1.27-alpine --overrides='{\"spec\":{\"nodeName\":\"$W\"}}'"
sleep 30
