#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
N="$(cq_node_name node01)"
ans() { grep -E "^$1=" "$CQ_WORK/116/answers.txt" 2>/dev/null | head -1 | cut -d= -f2- | tr -d ' \r'; }
E_CRI="$(cq_node_sh node01 'sed -n "s/^containerRuntimeEndpoint: *//p" /var/lib/kubelet/config.yaml')"
E_CNI="$(cq_node_sh node01 'ls /etc/cni/net.d | grep -E "\.conf(list)?$" | sort | head -1')"
E_PLUGIN="$(cq_node_sh node01 "grep -m1 '\"type\"' /etc/cni/net.d/$E_CNI" | sed -E 's/.*"type": *"([^"]+)".*/\1/')"
E_RT="$(kubectl get node "$N" -o jsonpath='{.status.nodeInfo.containerRuntimeVersion}')"
E_CIDR="$(kubectl get node "$N" -o jsonpath='{.spec.podCIDR}')"
E_CSI="$(kubectl get csidriver --no-headers 2>/dev/null | wc -l)"
check "answers.txt exists" file_exists "$CQ_WORK/116/answers.txt"
check "cri_endpoint is right" out_eq "$E_CRI" ans cri_endpoint
check "runtime is right" out_eq "$E_RT" ans runtime
check "cni_config is right" out_eq "$E_CNI" ans cni_config
check "cni_plugin is right" out_eq "$E_PLUGIN" ans cni_plugin
check "pod_cidr is right" out_eq "$E_CIDR" ans pod_cidr
check "csi_drivers is right" out_eq "$E_CSI" ans csi_drivers
finish
