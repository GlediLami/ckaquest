# The Route Goes Nowhere

## What happened
The route pointed at a Gateway that does not exist (`web-gateway`), so no controller picked it up. It also pointed at port 8080, but the Service listens on 80. The container port does not matter to a route. Only the Service port does.

## How to read route status
- No `status.parents` at all: no Gateway accepted the route. Check the parentRef name and namespace.
- `Accepted: False, reason NotAllowedByListeners`: the listener's `allowedRoutes` does not include this namespace.
- `ResolvedRefs: False, reason BackendNotFound`: wrong Service name or port.

## Exam angle
- Troubleshooting a route is a likely task. `k describe` first, then fix.
- `backendRefs.port` is the Service port, like `service.port.number` in an Ingress.

Bookmark: https://kubernetes.io/docs/concepts/services-networking/gateway/

Your notes: Gateway API, Network Troubleshooting
