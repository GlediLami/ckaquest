# Solution

```bash
ssh bare-controlplane
vim /root/calico.yaml
#            - name: CALICO_IPV4POOL_CIDR
#              value: "10.50.0.0/16"
kubectl apply -f /root/calico.yaml
kubectl get pods -n kube-system -w
kubectl get nodes
```
