#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
check 2 "package cri-dockerd is installed" node_ok bare-node01 'dpkg-query -W -f="\${Status}" cri-dockerd 2>/dev/null | grep -q "install ok installed"'
check "service cri-docker is enabled" node_ok bare-node01 '[ "$(systemctl is-enabled cri-docker)" = enabled ]'
check 2 "service cri-docker is running" node_ok bare-node01 'systemctl is-active -q cri-docker && test -e /run/cri-dockerd.sock'
check "ip_forward = 1 in /etc/sysctl.d" node_ok bare-node01 'cat /etc/sysctl.d/*.conf | grep -Eq "^net.ipv4.ip_forward *= *1"'
check "ipv6 forwarding = 1 in /etc/sysctl.d" node_ok bare-node01 'cat /etc/sysctl.d/*.conf | grep -Eq "^net.ipv6.conf.all.forwarding *= *1"'
check 2 "both are 1 right now" node_ok bare-node01 '[ "$(sysctl -n net.ipv4.ip_forward)$(sysctl -n net.ipv6.conf.all.forwarding)" = 11 ]'
finish
