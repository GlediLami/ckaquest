```bash
kubectl -n proxy-lab get endpointslices                 # endpoints are there
kubectl -n kube-system get pods -l k8s-app=kube-proxy    # CrashLoopBackOff
kubectl -n kube-system logs -l k8s-app=kube-proxy --tail=5
# open /var/lib/kube-proxy/kube-proxy.conf: no such file or directory
kubectl -n kube-system get cm kube-proxy -o yaml        # key: config.conf
kubectl -n kube-system edit ds kube-proxy               # --config=/var/lib/kube-proxy/config.conf
kubectl run t --rm -it --image=busybox:1.36 --restart=Never -n proxy-lab -- wget -qO- echo
```
