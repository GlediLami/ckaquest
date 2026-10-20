#!/usr/bin/env bash
set -uo pipefail
source "$CQ_ROOT/lib/common.sh"
cq_node_sh controlplane 'mkdir -p /opt/course/70 /root/.cq-trash; mv -f /opt/course/70/join.sh /root/.cq-trash/ 2>/dev/null || true'
