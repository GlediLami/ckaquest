#!/usr/bin/env bash
set -uo pipefail
source "$CQ_ROOT/lib/common.sh"
"$CQ_ROOT/cluster/stages.sh" bare fresh
"$CQ_ROOT/cluster/stages.sh" bare init
source "$CQ_ROOT/cluster/versions.env"
for f in tigera-operator.yaml custom-resources.yaml; do
  if [ -s "$CQ_HOME/offline/manifests/$f" ]; then
    docker cp "$CQ_HOME/offline/manifests/$f" "$(cq_node_name bare-controlplane):/root/$f" >/dev/null
  else
    cq_node_sh bare-controlplane "curl -fsSL -o /root/$f https://raw.githubusercontent.com/projectcalico/calico/$CALICO_VERSION/manifests/$f"
  fi
done
