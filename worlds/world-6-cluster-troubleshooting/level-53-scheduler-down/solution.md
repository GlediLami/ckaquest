```bash
kubectl -n sched-lab describe pod -l app=web     # Pending, no events
kubectl -n kube-system get pods                  # kube-scheduler CrashLoopBackOff / RunContainerError
kubectl -n kube-system describe pod kube-scheduler-ckaquest-control-plane
# exec: "kube-schedular": executable file not found
ssh controlplane
vim /etc/kubernetes/manifests/kube-scheduler.yaml   # command: - kube-scheduler
exit
kubectl -n sched-lab get pods -w
```
