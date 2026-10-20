```bash
kubectl -n cm-lab get deploy,rs,pods        # deploy 0/3, no rs
kubectl -n kube-system get pods             # controller-manager CrashLoopBackOff
kubectl -n kube-system logs kube-controller-manager-ckaquest-control-plane
# stat /etc/kubernetes/controller-manager.config: no such file or directory
ssh controlplane
ls /etc/kubernetes/*.conf
vim /etc/kubernetes/manifests/kube-controller-manager.yaml   # --kubeconfig=/etc/kubernetes/controller-manager.conf
exit
kubectl -n cm-lab get pods -w
```
