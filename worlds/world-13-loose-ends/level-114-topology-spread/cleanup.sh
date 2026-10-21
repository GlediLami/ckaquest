#!/usr/bin/env bash
source "$CQ_ROOT/lib/common.sh"
for n in node01 node02; do kubectl label node "$(cq_node_name $n)" topology.kubernetes.io/zone- >/dev/null 2>&1; done
true
