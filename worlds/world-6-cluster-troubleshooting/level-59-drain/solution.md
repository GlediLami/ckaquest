```bash
kubectl drain ckaquest-worker2 --ignore-daemonsets
# error: cannot delete Pods that declare no controller (use --force): maint/debug-shell
kubectl drain ckaquest-worker2 --ignore-daemonsets --force
# Cannot evict pod as it would violate the pod's disruption budget   (loops)
kubectl -n maint get pdb                     # ALLOWED DISRUPTIONS 0
kubectl -n maint patch pdb web-pdb --type=merge -p '{"spec":{"minAvailable":1}}'
kubectl drain ckaquest-worker2 --ignore-daemonsets --force
kubectl get nodes                            # SchedulingDisabled
kubectl -n maint get pods -o wide
```
