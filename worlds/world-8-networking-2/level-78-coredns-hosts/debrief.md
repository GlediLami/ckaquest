# A Name CoreDNS Does Not Know

## What happened
CoreDNS runs plugins in a fixed order for every query. `hosts` answers from a static list. Without `fallthrough` it would answer NXDOMAIN for every other name it does not know, and the cluster would break.

## Other common Corefile edits
- `forward . 8.8.8.8` changes the upstream resolver.
- A stub domain: a new server block `corp.local:53 { forward . 10.0.0.53 }`.
- `rewrite name foo.example.com foo.default.svc.cluster.local` aliases a name.

## Exam angle
- Back up the ConfigMap before you edit: `k get cm coredns -n kube-system -o yaml > coredns-backup.yaml`.
- The `reload` plugin picks up changes in about 30 seconds. A rollout restart is faster.

Bookmark: https://kubernetes.io/docs/tasks/administer-cluster/dns-custom-nameservers/

Your notes: DNS in Kubernetes
