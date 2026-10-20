#!/usr/bin/env bash
set -uo pipefail
source "$CQ_ROOT/lib/common.sh"
"$CQ_ROOT/cluster/stages.sh" bare init
cq_node_sh bare-controlplane "test -s /root/calico.yaml || curl -fsSL -o /root/calico.yaml https://raw.githubusercontent.com/projectcalico/calico/$(grep ^CALICO_VERSION "$CQ_ROOT/cluster/versions.env" | cut -d= -f2)/manifests/calico.yaml"
