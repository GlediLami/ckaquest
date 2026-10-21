#!/usr/bin/env bash
source "$CQ_ROOT/lib/common.sh"
cq_node_sh bare-node01 'dpkg -i /root/pkgs/cri-dockerd_0.3.20-ckaquest_all.deb >/dev/null
systemctl daemon-reload
systemctl enable --now cri-docker
printf "net.ipv4.ip_forward = 1\nnet.ipv6.conf.all.forwarding = 1\n" > /etc/sysctl.d/99-cri.conf
sysctl --system >/dev/null 2>&1; true'
