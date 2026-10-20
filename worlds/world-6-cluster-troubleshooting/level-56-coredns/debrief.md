# Names Do Not Resolve

## What happened
The Corefile served the zone `cluster.locl`. Queries for `cluster.local` fell through to the upstream resolver, which knows nothing about your Services. The pods were Running and Ready, so only the config showed the bug.

## DNS debugging order
1. From a pod: `nslookup kubernetes.default`. Use `busybox:1.28`, newer busybox nslookup is unreliable.
2. `cat /etc/resolv.conf` in the pod. The nameserver must be the `kube-dns` Service IP.
3. `kubectl -n kube-system get pods,svc,endpointslices -l k8s-app=kube-dns`.
4. `kubectl -n kube-system get cm coredns -o yaml`. Check the `kubernetes` plugin zone and `forward`.
5. CoreDNS logs.

## Names to know
- Service: `<svc>.<ns>.svc.cluster.local`
- Pod: `<ip-with-dashes>.<ns>.pod.cluster.local`
- Headless StatefulSet pod: `<pod>.<svc>.<ns>.svc.cluster.local`

## Your notes
- 11 Networking / DNS in Kubernetes
- 14 Troubleshooting / Network Troubleshooting
