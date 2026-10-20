# Solution

```bash
ssh bare-controlplane
kubeadm init --pod-network-cidr=10.50.0.0/16
mkdir -p $HOME/.kube
cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
kubectl get nodes          # NotReady until a CNI is installed
```
