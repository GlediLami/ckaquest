#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
token() { cq_node_sh controlplane "grep -o -- '--token [a-z0-9.]*' /opt/course/70/join.sh | cut -d' ' -f2"; }
listed() { local t; t="$(token)"; [ -n "$t" ] && cq_node_sh controlplane "kubeadm token list | grep -q '^$t'"; }
ttl_ok() { local t; t="$(token)"; cq_node_sh controlplane "kubeadm token list | grep '^$t' | awk '{print \$2}'" | grep -Eq '^(1h[0-9]+m|2h|1h)'; }
check "join.sh has a kubeadm join command" node_ok controlplane 'grep -q "kubeadm join .*--discovery-token-ca-cert-hash sha256:" /opt/course/70/join.sh'
check 2 "the token in join.sh exists" listed
check 2 "the token expires in about 2 hours" ttl_ok
finish
