#!/usr/bin/env bash
source "$CQ_ROOT/lib/common.sh"
t="$(cq_node_sh controlplane "grep -o -- '--token [a-z0-9.]*' /opt/course/70/join.sh 2>/dev/null | cut -d' ' -f2")"
[ -n "$t" ] && cq_node_sh controlplane "kubeadm token delete $t" >/dev/null 2>&1
true
true
