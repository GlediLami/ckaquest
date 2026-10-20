# 80/20

## What happened
`weight` on backendRefs splits traffic per request. With plain Services you could only split by pod count (level 18). Here the split is exact and independent of replicas.

## Facts to remember
- Weights are relative. 80/20, 8/2 and 4/1 are the same.
- Weight 0 sends nothing to that backend. Handy for a quick rollback.
- No weight means 1.

## Exam angle
- Canary and blue/green with Gateway API is a natural exam task.
- Ingress has no standard weights. It needs controller annotations, which is why Gateway API exists.

Bookmark: https://gateway-api.sigs.k8s.io/guides/traffic-splitting/

Your notes: Gateway API
