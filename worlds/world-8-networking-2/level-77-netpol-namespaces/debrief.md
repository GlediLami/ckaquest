# Only the Frontend Team

## What happened
`namespaceSelector` matches namespaces by label. Kubernetes adds `kubernetes.io/metadata.name` to every namespace, so you can select one by name without labelling it.

## AND versus OR
```yaml
from:
- namespaceSelector: {...}     # item 1
  podSelector: {...}           # same item: namespace AND pod must match
- podSelector: {...}           # item 2: OR this
```
One dash too many or too few changes the meaning. This is the most common NetworkPolicy mistake.

## Exam angle
- A policy only isolates the pods it selects, and only in the directions in `policyTypes`.
- Test with `k run t -n <ns> --rm -it --image=busybox:1.36 -- nc -zv -w2 <svc>.<ns> <port>`.

Bookmark: https://kubernetes.io/docs/concepts/services-networking/network-policies/

Your notes: Network Policy
