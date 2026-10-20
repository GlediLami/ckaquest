# Defaults for Everyone

## What happened
LimitRange is an admission plugin. At pod creation it fills in missing requests and limits, and rejects values outside min and max. Existing pods are not touched.

## LimitRange and ResourceQuota
- LimitRange: per container or pod, defaults and bounds.
- ResourceQuota: total for the namespace. A quota on requests forces every pod to have requests, so the two are often used together.

## Exam angle
- `default` is the limit. `defaultRequest` is the request. The names are easy to swap.

Bookmark: https://kubernetes.io/docs/concepts/policy/limit-range/

Your notes: Resource Requirements, Admission Controllers
