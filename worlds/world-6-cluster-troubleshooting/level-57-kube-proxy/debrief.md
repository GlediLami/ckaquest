# Services Stopped Routing

## What happened
The kube-proxy DaemonSet pointed to a config file name that is not in its ConfigMap. Every kube-proxy pod crashed. Old Services kept working for a while because their iptables rules were still on the nodes. New Services got no rules, so their ClusterIP went nowhere.

## How a ClusterIP works
A ClusterIP is not on any interface. kube-proxy on every node watches Services and EndpointSlices and writes iptables (or nftables / IPVS) rules. They rewrite the virtual IP to a pod IP. No kube-proxy, no translation.

## Service debugging order
1. `kubectl get svc,endpointslices -n <ns>`. No endpoints means a selector or readiness problem.
2. Endpoints fine but no answer: test a pod IP directly. If that works, suspect kube-proxy.
3. `kubectl -n kube-system get ds kube-proxy` and its logs. On a node: `iptables-save | grep <svc-name>`.
4. Port mismatch: `port` vs `targetPort` vs the container port.

## Your notes
- 11 Networking / Service Networking
- 2 Components / Worker Node / kube-proxy
- 14 Troubleshooting / Network Troubleshooting
