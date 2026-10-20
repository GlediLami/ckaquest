# Solution

```bash
ssh controlplane
kubeadm token create --ttl 2h --print-join-command > /opt/course/70/join.sh
kubeadm token list
```
