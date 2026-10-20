```bash
mkdir -p ~/ckaquest-work/58
kubectl top pod -n top-lab --sort-by=cpu
kubectl top pod -n top-lab --sort-by=cpu --no-headers | head -1 | awk '{print $1}' > ~/ckaquest-work/58/cpu-hog.txt
kubectl top node --sort-by=cpu --no-headers | head -1 | awk '{print $1}' > ~/ckaquest-work/58/busy-node.txt
kubectl patch pod report-generator -n top-lab --subresource resize \
  -p '{"spec":{"containers":[{"name":"worker","resources":{"limits":{"cpu":"100m"}}}]}}'
kubectl get pod report-generator -n top-lab -o jsonpath='{.status.containerStatuses[0].resources}'
```
