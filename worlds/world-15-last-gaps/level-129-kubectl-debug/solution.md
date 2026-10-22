# Solution

```bash
k debug api -n debug-lab -it --image=busybox:1.36 --target=api -- sh
# inside:
tr '\0' '\n' < /proc/1/environ | grep API_TOKEN
exit
echo <value> > ~/ckaquest-work/129/token.txt

k get nodes                                        # node01's real name
k debug node/<node01> -n debug-lab -it --image=busybox:1.36
# inside:
grep staticPodPath /host/var/lib/kubelet/config.yaml
exit
echo /etc/kubernetes/manifests > ~/ckaquest-work/129/staticpodpath.txt
```
