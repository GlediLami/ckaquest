# A Service Without a Selector

## What happened
Normally the EndpointSlice controller watches the Service's selector and writes the matching pod IPs into EndpointSlices. Without a selector, nothing does that. You write the EndpointSlice yourself and kube-proxy routes to whatever addresses it lists.

kube-proxy connects the two by the label `kubernetes.io/service-name` and by the **port name**. The Service port 80 named `http` sends traffic to the slice port named `http`, here 5678.

## When to use it
- A database outside the cluster, or in another cluster.
- Moving a workload into Kubernetes step by step.
- `type: ExternalName` is the DNS-only alternative. It returns a CNAME and has no ports.

## Gotchas
- The IP is static. If the pod restarts with a new IP, the slice is stale.
- The older `Endpoints` object still works but is deprecated. Use `EndpointSlice`.

## Exam angle
- "Use ClusterIP, NodePort, LoadBalancer service types and **endpoints**" is in the curriculum. A selectorless Service is the classic endpoints task.

Bookmark: https://kubernetes.io/docs/concepts/services-networking/service/#services-without-selectors

Your notes: Services
