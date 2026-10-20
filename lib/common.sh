#!/usr/bin/env bash
# Shared helpers for CKAQuest scripts. Source it, do not execute it.
#
# Isolation rule: every script works against the dedicated CKAQuest
# kubeconfig. Nothing here reads or writes ~/.kube/config.

CQ_ROOT="${CQ_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
CQ_HOME="${CQ_HOME:-$HOME/.ckaquest}"
CQ_WORK="${CQ_WORK:-$HOME/ckaquest-work}"
CQ_CLUSTER="${CQ_CLUSTER:-ckaquest}"
CQ_LAB_CLUSTER="${CQ_LAB_CLUSTER:-ckaquest-lab}"
CQ_CONTEXT="kind-${CQ_CLUSTER}"
CQ_LAB_CONTEXT="kind-${CQ_LAB_CLUSTER}"
CQ_NAMESPACE="${NAMESPACE:-ckaquest}"
CQ_KIND="${CQ_KIND:-kind}"
[ -x "$CQ_ROOT/.tools/kind" ] && CQ_KIND="$CQ_ROOT/.tools/kind"

export KUBECONFIG="${CKAQUEST_KUBECONFIG:-$CQ_HOME/kubeconfig}"
# Helm repos and releases cache stay inside CKAQuest, not in your own ~/.config/helm
export HELM_CONFIG_HOME="$CQ_HOME/helm/config" HELM_CACHE_HOME="$CQ_HOME/helm/cache" HELM_DATA_HOME="$CQ_HOME/helm/data"
export CQ_ROOT CQ_HOME CQ_WORK CQ_CLUSTER CQ_LAB_CLUSTER CQ_CONTEXT CQ_LAB_CONTEXT CQ_KIND

# Exam-style node names mapped to kind node containers.
cq_node_container() {
  case "$1" in
    controlplane|cluster1-controlplane) echo "${CQ_CLUSTER}-control-plane" ;;
    node01|cluster1-node01)             echo "${CQ_CLUSTER}-worker" ;;
    node02|cluster1-node02)             echo "${CQ_CLUSTER}-worker2" ;;
    lab-controlplane|cluster2-controlplane) echo "${CQ_LAB_CLUSTER}-control-plane" ;;
    lab-node01|cluster2-node01)         echo "${CQ_LAB_CLUSTER}-worker" ;;
    bare-controlplane)                  echo "${CQ_CLUSTER}-bare-cp" ;;
    bare-node01)                        echo "${CQ_CLUSTER}-bare-worker" ;;
    "${CQ_CLUSTER}"-*|"${CQ_LAB_CLUSTER}"-*) echo "$1" ;;
    *) return 1 ;;
  esac
}

# Run a command on a node: cq_node_exec node01 systemctl stop kubelet
cq_node_exec() {
  local container
  container="$(cq_node_container "$1")" || { echo "unknown node: $1" >&2; return 1; }
  shift
  docker exec "$container" "$@"
}

# Run a shell snippet on a node: cq_node_sh controlplane 'cat /etc/hosts | head'
cq_node_sh() {
  local node="$1"; shift
  cq_node_exec "$node" bash -c "$*"
}

# Copy a local file onto a node: cq_node_put node01 ./file /root/file
cq_node_put() {
  local container
  container="$(cq_node_container "$1")" || return 1
  docker cp "$2" "$container:$3" >/dev/null
}

# Kubernetes node name for an exam-style alias (node01 -> ckaquest-worker)
cq_node_name() { cq_node_container "$1"; }

cq_ensure_namespace() {
  kubectl create namespace "$1" --dry-run=client -o yaml | kubectl apply -f - >/dev/null
}

# Wait until a command succeeds: cq_wait 60 kubectl get ns foo
cq_wait() {
  local timeout="$1"; shift
  local end=$((SECONDS + timeout))
  until "$@" >/dev/null 2>&1; do
    [ "$SECONDS" -ge "$end" ] && return 1
    sleep 2
  done
}

cq_api_up() { kubectl get --raw=/readyz --request-timeout=5s >/dev/null 2>&1; }

cq_work_dir() {
  mkdir -p "$CQ_WORK/$1"
  echo "$CQ_WORK/$1"
}

# Back up a file on a node once, so cleanup can always restore the original.
cq_node_backup() {
  local node="$1" file="$2"
  cq_node_sh "$node" "mkdir -p /root/.cq-backup && [ -f /root/.cq-backup/$(basename "$file") ] || cp -a '$file' /root/.cq-backup/$(basename "$file")"
}

cq_node_restore() {
  local node="$1" file="$2"
  cq_node_sh "$node" "[ -f /root/.cq-backup/$(basename "$file") ] && cp -a /root/.cq-backup/$(basename "$file") '$file' && rm -f /root/.cq-backup/$(basename "$file") || true"
}

# Wait for the API server to answer (after a control plane change). Default 180s.
cq_wait_api() { cq_wait "${1:-180}" cq_api_up; }

# Patch a static pod manifest on the control plane with sed, keeping a backup.
# cq_break_manifest kube-scheduler 's/foo/bar/'
cq_break_manifest() {
  local component="$1" expr="$2"
  local file="/etc/kubernetes/manifests/${component}.yaml"
  cq_node_backup controlplane "$file"
  cq_node_sh controlplane "sed -i '$expr' '$file'"
}

cq_restore_manifest() {
  cq_node_restore controlplane "/etc/kubernetes/manifests/${1}.yaml"
}
