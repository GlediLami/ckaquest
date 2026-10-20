# Solution

```bash
k --context kind-ckaquest-lab drain <worker> --ignore-daemonsets
ssh lab-node01
apt-get update
apt-get install -y kubeadm='1.37.1-*'
kubeadm upgrade node
apt-get install -y kubelet='1.37.1-*' kubectl='1.37.1-*'
systemctl daemon-reload && systemctl restart kubelet
exit
k --context kind-ckaquest-lab uncordon <worker>
```
