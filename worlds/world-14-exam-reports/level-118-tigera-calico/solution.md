# Solution

```bash
ssh bare-controlplane
kubectl create -f /root/tigera-operator.yaml
grep cluster-cidr /etc/kubernetes/manifests/kube-controller-manager.yaml   # 10.50.0.0/16
vi /root/custom-resources.yaml        # ipPools[0].cidr: 10.50.0.0/16
kubectl create -f /root/custom-resources.yaml
watch kubectl get tigerastatus,pods -A
kubectl get nodes                     # Ready
```
