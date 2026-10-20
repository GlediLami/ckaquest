```bash
kubectl get nodes                  # connection refused
ssh controlplane
crictl ps -a | grep kube-apiserver # Exited, restarting
crictl logs <id> 2>&1 | tail       # dial tcp 127.0.0.1:2397: connect: connection refused
grep listen-client /etc/kubernetes/manifests/etcd.yaml   # 2379
vim /etc/kubernetes/manifests/kube-apiserver.yaml        # --etcd-servers=https://127.0.0.1:2379
watch crictl ps                    # wait for kube-apiserver Running
exit
kubectl get nodes
```
