#!/usr/bin/env bash
set -uo pipefail
source "$CQ_ROOT/lib/common.sh"
"$CQ_ROOT/cluster/stages.sh" bare fresh
cq_node_sh bare-node01 'set -e
d=/root/.cq-build/cri-dockerd
mkdir -p $d/DEBIAN $d/usr/bin $d/lib/systemd/system /root/pkgs
cat > $d/DEBIAN/control <<EOF
Package: cri-dockerd
Version: 0.3.20-ckaquest
Architecture: all
Maintainer: CKAQuest
Description: CKAQuest practice package that stands in for cri-dockerd
EOF
cat > $d/usr/bin/cri-dockerd <<"EOF"
#!/bin/sh
# Practice stand-in. It only holds the socket path the real cri-dockerd serves.
rm -f /run/cri-dockerd.sock
touch /run/cri-dockerd.sock
exec sleep infinity
EOF
chmod 755 $d/usr/bin/cri-dockerd
cat > $d/lib/systemd/system/cri-docker.service <<EOF
[Unit]
Description=CRI interface for Docker (CKAQuest practice package)

[Service]
ExecStart=/usr/bin/cri-dockerd
Restart=always

[Install]
WantedBy=multi-user.target
EOF
dpkg-deb --build $d /root/pkgs/cri-dockerd_0.3.20-ckaquest_all.deb >/dev/null
sysctl -qw net.ipv4.ip_forward=0 net.ipv6.conf.all.forwarding=0'
