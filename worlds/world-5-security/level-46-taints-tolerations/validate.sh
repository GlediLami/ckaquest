#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
N1="$(cq_node_name node01)"
tainted() { jp - "node/$1" '{.spec.taints[?(@.key=="dedicated")].effect}' | grep -q NoSchedule; }
toleration() { jp taints-tolerations pod/regular-app '{.spec.tolerations[?(@.key=="dedicated")]}'; }
check "node01 keeps its dedicated taint" tainted "$N1"
check "regular-app still selects node01" field_eq taints-tolerations pod/regular-app '{.spec.nodeSelector.kubernetes\.io/hostname}' "$N1"
check 2 "regular-app tolerates dedicated=gpu:NoSchedule" out_match '"effect":"NoSchedule"' toleration
check 2 "regular-app is Running on node01" field_eq taints-tolerations pod/regular-app '{.status.phase}/{.spec.nodeName}' "Running/$N1"
finish
