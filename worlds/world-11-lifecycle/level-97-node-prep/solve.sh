#!/usr/bin/env bash
source "$CQ_ROOT/lib/common.sh"
for n in bare-controlplane bare-node01; do
cq_node_sh $n 'printf "overlay\nbr_netfilter\n" > /etc/modules-load.d/k8s.conf
printf "net.ipv4.ip_forward = 1\nnet.bridge.bridge-nf-call-iptables = 1\nnet.bridge.bridge-nf-call-ip6tables = 1\n" > /etc/sysctl.d/k8s.conf
sysctl --system >/dev/null 2>&1; true'
done
