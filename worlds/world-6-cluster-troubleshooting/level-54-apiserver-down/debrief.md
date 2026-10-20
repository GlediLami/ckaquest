# The API Server Is Gone

## What happened
`--etcd-servers` pointed to a wrong port. The API server cannot start without etcd. It exits, the kubelet restarts it, it exits again. kubectl has nothing to talk to.

## Debugging without kubectl
On the control plane node:
- `crictl ps -a` lists all containers, also exited ones. Look at the ATTEMPT column.
- `crictl logs <container-id>` shows the last output of a container.
- `/var/log/pods/<ns>_<pod>_<uid>/<container>/` keeps log files even when the container is gone.
- `journalctl -u kubelet | grep apiserver` shows if the kubelet cannot even parse the manifest (YAML error). Then no container is created at all.

## Typical API server faults in the exam
- Wrong etcd port or IP, or wrong etcd cert paths (`--etcd-cafile`, `--etcd-certfile`).
- Typo in a flag name. The process exits with "unknown flag".
- Broken YAML indentation. No container at all. Only the kubelet log helps.
- Wrong `--advertise-address` or a missing volume mount for a cert.

## Ports to remember
- 6443: API server
- 2379: etcd clients, 2380: etcd peers
- 10250: kubelet, 10257: controller-manager, 10259: scheduler

## Your notes
- 14 Troubleshooting / Control Plane Failure
- 2 Components / Control Plane / kube-apiserver, etcd
