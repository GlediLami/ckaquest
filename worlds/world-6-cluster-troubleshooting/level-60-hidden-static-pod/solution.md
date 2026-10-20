```bash
kubectl get pods -n default -o wide          # crypto-miner-ckaquest-worker on ckaquest-worker
kubectl get pod crypto-miner-ckaquest-worker -o jsonpath='{.metadata.ownerReferences[0].kind}'   # Node
ssh node01
ps -ef | grep kubelet | grep -o -- '--config=[^ ]*'
grep staticPodPath /var/lib/kubelet/config.yaml   # /etc/kubelet.d
rm /etc/kubelet.d/miner.yaml
exit
kubectl get pods -n default -w
```
