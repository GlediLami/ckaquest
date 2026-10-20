# Solution

```bash
ssh controlplane
kubectl get nodes                   # error: context "kubernetes-admin@kubernetez" does not exist
kubectl config get-contexts
kubectl config use-context kubernetes-admin@ckaquest
kubectl get nodes                   # connection refused on :6444
ss -lntp | grep apiserver           # 6443
vim /root/.kube/config              # server: https://...:6443
kubectl get nodes
```
