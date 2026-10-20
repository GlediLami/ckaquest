# Solution

```bash
ssh bare-controlplane
kubeadm token create --print-join-command
exit
ssh bare-node01
kubeadm join <ip>:6443 --token ... --discovery-token-ca-cert-hash sha256:...
exit
ssh bare-controlplane
kubectl get nodes
kubectl run hello --image=nginx:1.27-alpine
kubectl get pod hello -o wide
```
