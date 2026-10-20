```bash
ssh node02
systemctl status kubelet          # activating (auto-restart)
journalctl -u kubelet --no-pager | tail -30
# ... unable to load client CA file /etc/kubernetes/pki/ca-cert.pem: no such file
ls /etc/kubernetes/pki/           # ca.crt
vim /var/lib/kubelet/config.yaml  # clientCAFile: /etc/kubernetes/pki/ca.crt
systemctl restart kubelet
```
