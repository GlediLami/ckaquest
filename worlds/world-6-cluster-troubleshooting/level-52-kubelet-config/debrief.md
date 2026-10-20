# Kubelet Will Not Start

## What happened
`clientCAFile` in `/var/lib/kubelet/config.yaml` pointed to a file that does not exist. The kubelet checks this at startup and exits. systemd restarts it every few seconds, so `systemctl status` shows `activating (auto-restart)`.

## Where the kubelet gets its settings
- The unit: `systemctl cat kubelet` shows the unit plus drop-ins in `/etc/systemd/system/kubelet.service.d/` (kubeadm puts `10-kubeadm.conf` there).
- `--config=/var/lib/kubelet/config.yaml`: the KubeletConfiguration (CA file, staticPodPath, cgroupDriver, clusterDNS).
- `--kubeconfig=/etc/kubernetes/kubelet.conf`: how the kubelet talks to the API server.
- `/var/lib/kubelet/kubeadm-flags.env`: extra flags written by kubeadm.

Typical exam faults in these files: wrong CA path, wrong API server port in kubelet.conf, wrong binary path in the drop-in. If you edit a unit or drop-in, run `systemctl daemon-reload` before the restart.

## Fast reading of logs
`journalctl -u kubelet -f` follows live. `journalctl -u kubelet --no-pager | grep -i error | tail` cuts the noise.

## Your notes
- 14 Troubleshooting / Worker Node Failure
- 2 Components / Worker Node / kubelet
