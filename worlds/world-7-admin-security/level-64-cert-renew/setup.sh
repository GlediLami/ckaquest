#!/usr/bin/env bash
set -uo pipefail
source "$CQ_ROOT/lib/common.sh"
cq_node_sh controlplane 'mkdir -p /opt/course/64 /root/.cq-backup
mv -f /opt/course/64/expiry-before.txt /root/.cq-backup/64-old-answer 2>/dev/null || true
openssl x509 -in /etc/kubernetes/pki/apiserver.crt -noout -enddate > /root/.cq-backup/64-enddate'
