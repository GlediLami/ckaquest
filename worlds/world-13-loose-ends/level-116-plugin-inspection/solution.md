# Solution

```bash
ssh node01
grep containerRuntimeEndpoint /var/lib/kubelet/config.yaml   # unix:///run/containerd/containerd.sock
ls /etc/cni/net.d                                           # 10-kindnet.conflist
grep -m1 '"type"' /etc/cni/net.d/10-kindnet.conflist        # ptp
exit
k get node node01 -o jsonpath='{.status.nodeInfo.containerRuntimeVersion}{"\n"}{.spec.podCIDR}{"\n"}'
k get csidriver --no-headers | wc -l
vi ~/ckaquest-work/116/answers.txt
```
