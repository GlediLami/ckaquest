# Solution

```bash
ssh lab-controlplane
apt-get update
apt-cache madison kubeadm | head -3
apt-get install -y kubeadm='1.37.1-*'
kubeadm version
kubeadm upgrade plan
kubeadm upgrade apply v1.37.1
kubectl drain lab-controlplane --ignore-daemonsets      # use the real node name
apt-get install -y kubelet='1.37.1-*' kubectl='1.37.1-*'
systemctl daemon-reload && systemctl restart kubelet
kubectl uncordon <node>
kubectl get nodes
```
