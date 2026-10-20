#!/usr/bin/env bash
# Brings the practice clusters of World 11 to a known stage, so every level can start alone.
#   stages.sh bare <fresh|init|cni|joined>   bare nodes (cq-cluster bare-up)
#   stages.sh lab  <fresh|cp-upgraded>       lab cluster (cq-cluster lab-up), apt repo for the target ready
set -euo pipefail
source "$(dirname "$0")/../lib/common.sh"
source "$CQ_ROOT/cluster/versions.env"
CQ="$CQ_ROOT/bin/cq-cluster"
POD_CIDR=10.50.0.0/16
TARGET="${LAB_UPGRADE_TARGET#v}"          # 1.37.1
MINOR="v${TARGET%.*}"                     # v1.37

bare() { cq_node_sh "bare-$1" "$2"; }
bare_kubectl() { bare controlplane "kubectl --kubeconfig /etc/kubernetes/admin.conf $*"; }
initialized() { bare controlplane 'test -f /etc/kubernetes/admin.conf' 2>/dev/null; }
has_cni() { bare_kubectl get ds calico-node -n kube-system >/dev/null 2>&1; }
joined() { bare_kubectl get node "$(cq_node_name bare-node01)" >/dev/null 2>&1; }

bare_fresh() { "$CQ" bare-down >/dev/null; "$CQ" bare-up >/dev/null; }
bare_init() {
  docker inspect "$(cq_node_name bare-controlplane)" >/dev/null 2>&1 || bare_fresh
  initialized && return 0
  bare controlplane "kubeadm init --pod-network-cidr=$POD_CIDR >/root/kubeadm-init.log 2>&1
mkdir -p /root/.kube && cp /etc/kubernetes/admin.conf /root/.kube/config"
}
calico_manifest() {
  local vendored="$CQ_HOME/offline/manifests/calico.yaml"
  if [ -s "$vendored" ]; then
    docker cp "$vendored" "$(cq_node_name bare-controlplane):/root/calico.yaml" >/dev/null
    return 0
  fi
  bare controlplane "test -s /root/calico.yaml || curl -fsSL -o /root/calico.yaml https://raw.githubusercontent.com/projectcalico/calico/$CALICO_VERSION/manifests/calico.yaml"
}
bare_cni() {
  bare_init
  has_cni && return 0
  calico_manifest
  bare controlplane "sed -e 's|# - name: CALICO_IPV4POOL_CIDR|- name: CALICO_IPV4POOL_CIDR|' -e 's|#   value: \"192.168.0.0/16\"|  value: \"$POD_CIDR\"|' /root/calico.yaml > /root/calico-cq.yaml
kubectl apply -f /root/calico-cq.yaml >/dev/null"
  cq_wait 300 bare_kubectl rollout status ds/calico-node -n kube-system --timeout=10s
}
bare_joined() {
  bare_cni
  joined && return 0
  local cmd; cmd="$(bare controlplane 'kubeadm token create --print-join-command')"
  bare node01 "$cmd >/dev/null 2>&1"
  local i
  for i in $(seq 40); do
    [ "$(bare_kubectl get nodes --no-headers | grep -c ' Ready')" = 2 ] && return 0
    sleep 5
  done
  return 1
}

lab_version() { kubectl --context "$CQ_LAB_CONTEXT" get node "$(cq_node_name lab-controlplane)" -o jsonpath='{.status.nodeInfo.kubeletVersion}' 2>/dev/null; }
lab_repo() {
  if [ -s "$CQ_HOME/offline/debs/Packages" ]; then
    # Offline: a local apt repo with the target .debs. The commands stay the same.
    for n in lab-controlplane lab-node01; do
      docker cp "$CQ_HOME/offline/debs/." "$(cq_node_name $n):/var/cache/cq-debs/" >/dev/null
      cq_node_sh "$n" "echo 'deb [trusted=yes] file:/var/cache/cq-debs ./' > /etc/apt/sources.list.d/kubernetes.list; apt-get update -qq -o Dir::Etc::sourceparts=/etc/apt/sources.list.d -o Dir::Etc::sourcelist=/dev/null >/dev/null 2>&1"
    done
    return 0
  fi
  for n in lab-controlplane lab-node01; do
    cq_node_sh "$n" "test -f /etc/apt/sources.list.d/kubernetes.list && exit 0
apt-get update -qq >/dev/null; apt-get install -y -qq curl gpg >/dev/null 2>&1
mkdir -p /etc/apt/keyrings
curl -fsSL https://pkgs.k8s.io/core:/stable:/$MINOR/deb/Release.key | gpg --dearmor --yes -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/$MINOR/deb/ /' > /etc/apt/sources.list.d/kubernetes.list
apt-get update -qq >/dev/null"
  done
}
lab_fresh() {
  if [ "$(lab_version)" != "${LAB_NODE_IMAGE_VERSION:-v1.36.4}" ]; then
    "$CQ" lab-down >/dev/null 2>&1 || true
    "$CQ" lab-up >/dev/null
  fi
  lab_repo
}
lab_cp_upgraded() {
  lab_fresh
  cq_node_sh lab-controlplane "kubeadm version -o short | grep -q v$TARGET || apt-get install -y -qq 'kubeadm=$TARGET-*' >/dev/null
kubectl get node \$(hostname) -o jsonpath='{.status.nodeInfo.kubeletVersion}' | grep -q v$TARGET && exit 0
kubeadm upgrade apply v$TARGET -y >/dev/null
kubectl drain \$(hostname) --ignore-daemonsets >/dev/null
apt-get install -y -qq 'kubelet=$TARGET-*' 'kubectl=$TARGET-*' >/dev/null
systemctl daemon-reload && systemctl restart kubelet
sleep 15; kubectl uncordon \$(hostname) >/dev/null"
}

case "${1:-}/${2:-}" in
  bare/fresh) bare_fresh ;;
  bare/init) bare_init ;;
  bare/cni) bare_cni ;;
  bare/joined) bare_joined ;;
  lab/fresh) lab_fresh ;;
  lab/cp-upgraded) lab_cp_upgraded ;;
  *) echo "usage: stages.sh bare <fresh|init|cni|joined> | lab <fresh|cp-upgraded>" >&2; exit 1 ;;
esac
