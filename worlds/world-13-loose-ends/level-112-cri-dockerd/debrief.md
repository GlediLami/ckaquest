# Another Runtime Socket

## What happened
The kubelet talks to a container runtime through the CRI, a gRPC API on a Unix socket. containerd and CRI-O speak CRI directly. Docker Engine does not, so since dockershim was removed in v1.24, Docker needs the adapter cri-dockerd. It serves `unix:///run/cri-dockerd.sock`.

A node uses it when the kubelet points there: `kubeadm init/join --cri-socket unix:///run/cri-dockerd.sock`, or `containerRuntimeEndpoint` in the kubelet config.

## The three steps
- `dpkg -i` installs. `dpkg -l | grep cri` and `dpkg -L <pkg>` check.
- `systemctl enable --now` makes the service start now and after a reboot. `enable` alone does not start it.
- `/etc/sysctl.d/*.conf` plus `sysctl --system` makes kernel settings both persistent and live.

## Exam angle
- People report this exact shape: install cri-dockerd from a .deb, start it, set sysctls. The values are given in the task.
- Check every part afterwards: `systemctl is-enabled`, `systemctl is-active`, `sysctl <key>`.

Bookmark: https://kubernetes.io/docs/setup/production-environment/container-runtimes/

Your notes: Cluster Install (course sections 10 and 11)
