#!/usr/bin/env bash
# Runs INSIDE a kind node (docker exec). Makes the node feel like an exam node:
# vim, bash completion, alias k, kubectl config on the control plane, etcdctl/etcdutl.
# Usage: node-bootstrap.sh <controlplane|worker|tools>
set -euo pipefail
role="${1:-worker}"
marker=/root/.cq-bootstrapped
# Role "tools" only installs the tools (used to build the offline node image, no cluster needed).

export DEBIAN_FRONTEND=noninteractive
# kind ships its own /etc/default/kubelet. Without this, "apt-get install kubelet" during an
# upgrade task stops at a dpkg config-file prompt.
echo 'Dpkg::Options { "--force-confold"; };' > /etc/apt/apt.conf.d/90ckaquest
if ! command -v vim >/dev/null; then
  apt-get update -qq >/dev/null
  apt-get install -y -qq --no-install-recommends vim less bash-completion iproute2 procps >/dev/null
fi
if ! command -v sudo >/dev/null; then
  apt-get update -qq >/dev/null
  apt-get install -y -qq --no-install-recommends sudo >/dev/null
fi

grep -q "CKAQuest exam-node setup" /root/.bashrc 2>/dev/null || cat >> /root/.bashrc <<'EOF'
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

if [ ! -x /usr/local/bin/etcdctl ]; then
  # etcdctl and etcdutl matching the etcd that kubeadm deploys for this node's version
  etcd_version="$(kubeadm config images list --kubernetes-version "$(kubeadm version -o short)" 2>/dev/null \
    | sed -nE 's|.*/etcd:([0-9.]+).*|\1|p')"
  arch="$(dpkg --print-architecture)"
  tmp="$(mktemp -d)"
  curl -sSL "https://github.com/etcd-io/etcd/releases/download/v${etcd_version}/etcd-v${etcd_version}-linux-${arch}.tar.gz" \
    | tar -xz -C "$tmp" --strip-components=1
  install -m 0755 "$tmp/etcdctl" "$tmp/etcdutl" /usr/local/bin/
fi

# Exam-style login user: like the real exam, root-only work needs sudo (CQ_NODE_USER=candidate)
if ! id candidate >/dev/null 2>&1; then
  useradd -m -s /bin/bash candidate
  echo 'candidate ALL=(ALL) NOPASSWD:ALL' > /etc/sudoers.d/candidate
  chmod 0440 /etc/sudoers.d/candidate
fi
sed -n '/# CKAQuest exam-node setup/,$p' /root/.bashrc > /home/candidate/.bashrc.cq
grep -q "bashrc.cq" /home/candidate/.bashrc 2>/dev/null || echo 'source ~/.bashrc.cq' >> /home/candidate/.bashrc
cp /root/.vimrc /home/candidate/.vimrc
chown candidate:candidate /home/candidate/.bashrc.cq /home/candidate/.vimrc

if [ "$role" = "controlplane" ]; then
  mkdir -p /root/.kube /home/candidate/.kube
  cp /etc/kubernetes/admin.conf /root/.kube/config
  cp /etc/kubernetes/admin.conf /home/candidate/.kube/config
  chown -R candidate:candidate /home/candidate/.kube
fi

touch "$marker"
