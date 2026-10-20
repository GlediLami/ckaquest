# Solution

```bash
ssh controlplane
openssl x509 -in /etc/kubernetes/pki/apiserver.crt -noout -enddate > /opt/course/64/expiry-before.txt
kubeadm certs check-expiration
kubeadm certs renew apiserver
mv /etc/kubernetes/manifests/kube-apiserver.yaml /root/
watch crictl ps          # wait until kube-apiserver is gone
mv /root/kube-apiserver.yaml /etc/kubernetes/manifests/
kubeadm certs check-expiration | grep apiserver
```
