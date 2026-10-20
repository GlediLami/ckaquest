#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
for n in bare-controlplane bare-node01; do
  check "$n: modules file loads overlay and br_netfilter" node_ok $n 'grep -qx overlay /etc/modules-load.d/k8s.conf && grep -qx br_netfilter /etc/modules-load.d/k8s.conf'
  check "$n: sysctl file has the 3 settings" node_ok $n 'f=/etc/sysctl.d/k8s.conf; grep -Eq "^net.ipv4.ip_forward *= *1" $f && grep -Eq "^net.bridge.bridge-nf-call-iptables *= *1" $f && grep -Eq "^net.bridge.bridge-nf-call-ip6tables *= *1" $f'
  check 2 "$n: ip_forward is 1 now" node_ok $n '[ "$(sysctl -n net.ipv4.ip_forward)" = 1 ]'
done
finish
