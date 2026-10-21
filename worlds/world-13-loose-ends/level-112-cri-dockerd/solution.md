# Solution

```bash
ssh bare-node01
dpkg -i /root/pkgs/cri-dockerd_0.3.20-ckaquest_all.deb
systemctl enable --now cri-docker
systemctl status cri-docker
cat <<EOF > /etc/sysctl.d/99-cri.conf
net.ipv4.ip_forward = 1
net.ipv6.conf.all.forwarding = 1
EOF
sysctl --system
sysctl net.ipv4.ip_forward net.ipv6.conf.all.forwarding
```
