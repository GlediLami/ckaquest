# Node NotReady

## What happened
The kubelet on node01 was stopped and disabled. The kubelet sends the node heartbeat (a Lease in `kube-node-lease`). When the heartbeat stops for longer than the grace period, the node controller marks the node `NotReady` (status Unknown). After a while it also adds the taint `node.kubernetes.io/unreachable` and pods get evicted.

## The exam runbook for a NotReady node
1. `kubectl get nodes` and `kubectl describe node <node>`. Read Conditions and Events.
2. `ssh <node>`.
3. `systemctl status kubelet`. Is it running? Is it enabled?
4. If it fails to start: `journalctl -u kubelet --no-pager | tail -50`.
5. Check the container runtime: `systemctl status containerd`, `crictl ps`.
6. Fix, then `systemctl daemon-reload` (only if you changed unit files) and `systemctl restart kubelet`.

## Exam trap
`systemctl start kubelet` fixes it now. The task says "survives a reboot". That needs `enable`. Read every word of the task. Partial fixes give partial points.

## Your notes
- 14 Troubleshooting / Worker Node Failure
- 2 Components / Worker Node / kubelet
