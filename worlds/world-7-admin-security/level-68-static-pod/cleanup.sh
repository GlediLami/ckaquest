#!/usr/bin/env bash
source "$CQ_ROOT/lib/common.sh"
cq_node_sh node01 'mkdir -p /root/.cq-trash; [ -f /etc/kubernetes/manifests/static-web.yaml ] && mv /etc/kubernetes/manifests/static-web.yaml /root/.cq-trash/static-web.$(date +%s).yaml || true'
true
