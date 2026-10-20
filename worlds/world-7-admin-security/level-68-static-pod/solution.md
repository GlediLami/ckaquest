# Solution

```bash
k run static-web -n static-lab --image=nginx:1.27-alpine --port=80 -l app=static-web $do > static-web.yaml
ssh node01
grep staticPodPath /var/lib/kubelet/config.yaml      # /etc/kubernetes/manifests
vim /etc/kubernetes/manifests/static-web.yaml        # paste the YAML
exit
k get pods -n static-lab -o wide
```
