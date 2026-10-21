#!/usr/bin/env bash
source "$CQ_ROOT/lib/common.sh"
N="$(cq_node_name node01)"
cni="$(cq_node_sh node01 'ls /etc/cni/net.d | grep -E "\.conf(list)?$" | sort | head -1')"
{
echo "cri_endpoint=$(cq_node_sh node01 'sed -n "s/^containerRuntimeEndpoint: *//p" /var/lib/kubelet/config.yaml')"
echo "runtime=$(kubectl get node "$N" -o jsonpath='{.status.nodeInfo.containerRuntimeVersion}')"
echo "cni_config=$cni"
echo "cni_plugin=$(cq_node_sh node01 "grep -m1 '\"type\"' /etc/cni/net.d/$cni" | sed -E 's/.*"type": *"([^"]+)".*/\1/')"
echo "pod_cidr=$(kubectl get node "$N" -o jsonpath='{.spec.podCIDR}')"
echo "csi_drivers=$(kubectl get csidriver --no-headers 2>/dev/null | wc -l)"
} > "$CQ_WORK/116/answers.txt"
