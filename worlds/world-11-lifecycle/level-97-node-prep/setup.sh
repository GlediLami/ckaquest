#!/usr/bin/env bash
set -uo pipefail
source "$CQ_ROOT/lib/common.sh"
"$CQ_ROOT/cluster/stages.sh" bare fresh
for n in bare-controlplane bare-node01; do cq_node_sh $n 'sysctl -qw net.ipv4.ip_forward=0'; done
