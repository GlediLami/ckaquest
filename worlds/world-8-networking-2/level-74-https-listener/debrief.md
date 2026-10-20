# HTTPS on the Gateway

## What happened
TLS belongs to the Gateway listener, not to the route. The listener terminates TLS with the Secret, then routes plain HTTP to the backend.

`sectionName` pins a route to one listener by name. The route was pinned to `http`, so the new HTTPS listener had no routes.

## Facts to remember
- `k create secret tls` gives type `kubernetes.io/tls` with keys `tls.crt` and `tls.key`.
- The Secret must be in the Gateway's namespace, or you need a ReferenceGrant.
- `mode: Passthrough` sends TLS through untouched (TLSRoute, not HTTPRoute).

## Exam angle
- Expect "add HTTPS" or "the HTTPS listener is not ready": check the Secret name, namespace and the listener status in `k describe gateway`.

Bookmark: https://gateway-api.sigs.k8s.io/guides/tls/

Your notes: Gateway API, TLS Basics
