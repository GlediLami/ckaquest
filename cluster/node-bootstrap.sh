#!/usr/bin/env bash
# Runs INSIDE a kind node (docker exec). Makes the node feel like an exam node:
# vim, bash completion, alias k, kubectl config on the control plane, etcdctl/etcdutl.
# Usage: node-bootstrap.sh <controlplane|worker>
set -euo pipefail
role="${1:-worker}"
marker=/root/.cq-bootstrapped
[ -f "$marker" ] && exit 0

export DEBIAN_FRONTEND=noninteractive
apt-get update -qq >/dev/null
apt-get install -y -qq --no-install-recommends vim less bash-completion iproute2 procps >/dev/null

cat >> /root/.bashrc <<'EOF'
# CKAQuest exam-node setup
source /usr/share/bash-completion/bash_completion 2>/dev/null
alias k=kubectl
source <(kubectl completion bash 2>/dev/null) 2>/dev/null
complete -o default -F __start_kubectl k 2>/dev/null
export do="--dry-run=client -o yaml"
export now="--force --grace-period 0"
EOF

cat > /root/.vimrc <<'EOF'
set expandtab
set tabstop=2
set shiftwidth=2
set number
syntax on
EOF

if [ "$role" = "controlplane" ]; then
  mkdir -p /root/.kube
  cp /etc/kubernetes/admin.conf /root/.kube/config
  # etcdctl and etcdutl matching the running etcd
  etcd_version="$(grep -m1 'image:' /etc/kubernetes/manifests/etcd.yaml | sed -E 's/.*etcd:([0-9.]+).*/\1/')"
  arch="$(dpkg --print-architecture)"
  tmp="$(mktemp -d)"
  curl -sSL "https://github.com/etcd-io/etcd/releases/download/v${etcd_version}/etcd-v${etcd_version}-linux-${arch}.tar.gz" \
    | tar -xz -C "$tmp" --strip-components=1
  install -m 0755 "$tmp/etcdctl" "$tmp/etcdutl" /usr/local/bin/
fi

touch "$marker"
