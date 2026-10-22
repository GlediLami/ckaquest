# Pick the Right Key

## What happened
NetworkPolicies are allow lists. Once a pod is selected by any policy for Ingress, only traffic that some policy allows gets in. Policies add up. They never subtract.

So "least permissive" means: the smallest set of sources and ports that still makes the required connection work.

## Reading a rule
- `podSelector` in `spec`: which pods the policy protects.
- `from.podSelector`: pods in the **same** namespace.
- `from.namespaceSelector: {}`: every pod in every namespace.
- `- {}` as an ingress rule: everything.
- no `ports`: all ports.
- `podSelector` and `namespaceSelector` in the **same** `from` item: AND. As two items: OR.

## Exam angle
- Reported: "several policy files are given, apply the least permissive one". Read them all before applying anything. Applying a wrong one and then a right one leaves both active.

Bookmark: https://kubernetes.io/docs/concepts/services-networking/network-policies/

Your notes: Network Policies
