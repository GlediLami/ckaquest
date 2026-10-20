```bash
kubectl run t --rm -it --image=busybox:1.28 --restart=Never -- nslookup web.dns-lab.svc.cluster.local
# server can't find ... NXDOMAIN
kubectl -n kube-system get pods -l k8s-app=kube-dns       # Running
kubectl -n kube-system logs -l k8s-app=kube-dns            # forwarding cluster.local upstream
kubectl -n kube-system edit cm coredns                     # cluster.locl -> cluster.local
kubectl -n kube-system rollout restart deploy coredns
```
