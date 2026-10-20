#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
all_nodes() { [ "$(jp agent-lab ds/node-agent '{.status.numberReady}')" = "$(kubectl get nodes --no-headers | wc -l | tr -d ' ')" ]; }
check 3 "node-agent runs ready on every node" all_nodes
check "requests are 10m / 16Mi" out_eq "10m 16Mi" kubectl get ds node-agent -n agent-lab -o jsonpath='{.spec.template.spec.containers[0].resources.requests.cpu} {.spec.template.spec.containers[0].resources.requests.memory}'
check "the control plane taint is not removed" out_match "node-role.kubernetes.io/control-plane" kubectl get node "$(cq_node_name controlplane)" -o jsonpath='{.spec.taints[*].key}'
finish
