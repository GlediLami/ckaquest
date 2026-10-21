# Solution

```bash
ssh bare-controlplane
ip -4 addr show eth0                                   # say 172.19.0.5
echo "172.19.0.5 k8s-api.ckaquest.local" >> /etc/hosts
kubeadm init --control-plane-endpoint=k8s-api.ckaquest.local:6443 \
  --pod-network-cidr=10.50.0.0/16 --upload-certs
mkdir -p ~/.kube && cp /etc/kubernetes/admin.conf ~/.kube/config

# copy the control plane join command from the output, or build it again:
KEY=$(kubeadm init phase upload-certs --upload-certs | tail -1)
kubeadm token create --print-join-command --certificate-key $KEY > /root/cp-join.sh
```
