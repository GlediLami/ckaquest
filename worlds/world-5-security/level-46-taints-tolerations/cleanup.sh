#!/usr/bin/env bash
source "$CQ_ROOT/lib/common.sh"
kubectl taint node "$(cq_node_name node01)" dedicated- >/dev/null 2>&1 || true
kubectl delete pod regular-app -n taints-tolerations --ignore-not-found --wait=false >/dev/null 2>&1
true
