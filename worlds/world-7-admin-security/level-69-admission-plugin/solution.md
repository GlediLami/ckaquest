# Solution

```bash
ssh controlplane
vim /etc/kubernetes/manifests/kube-apiserver.yaml
#   - --enable-admission-plugins=NodeRestriction,NamespaceAutoProvision
watch crictl ps            # wait for kube-apiserver
exit
k run probe -n auto-created --image=busybox:1.36 -- sleep 3600
k get ns auto-created
```
