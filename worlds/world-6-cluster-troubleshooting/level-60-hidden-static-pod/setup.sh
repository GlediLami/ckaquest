#!/usr/bin/env bash
set -euo pipefail
source "$CQ_ROOT/lib/common.sh"
cq_node_backup node01 /var/lib/kubelet/config.yaml
cq_node_sh node01 '
  mkdir -p /etc/kubelet.d
  sed -i "s|staticPodPath: /etc/kubernetes/manifests|staticPodPath: /etc/kubelet.d|" /var/lib/kubelet/config.yaml
  cat > /etc/kubelet.d/miner.yaml <<YAML
apiVersion: v1
kind: Pod
metadata:
  name: crypto-miner
  namespace: default
spec:
  containers:
  - name: miner
    image: busybox:1.36
    command: ["sh", "-c", "while true; do sleep 3600; done"]
YAML
  systemctl restart kubelet'
cq_wait 120 kubectl get pod crypto-miner-ckaquest-worker -n default
