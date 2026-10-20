```bash
kubectl get nodes                       # ckaquest-worker NotReady
kubectl describe node ckaquest-worker   # "Kubelet stopped posting node status"
ssh node01
systemctl status kubelet                # inactive (dead), disabled
systemctl enable --now kubelet
exit
kubectl get nodes -w                    # Ready after a few seconds
```
