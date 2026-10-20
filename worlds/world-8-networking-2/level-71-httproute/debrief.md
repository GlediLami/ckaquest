# First Route Through the Gateway

## What happened
Gateway API splits the old Ingress into roles:
- **GatewayClass**: which controller (here NGINX Gateway Fabric, class `nginx`). Set up by the platform team.
- **Gateway**: the listeners (ports, protocols, TLS). Owned by the cluster operator.
- **HTTPRoute**: host and path rules to Services. Owned by the app team.

## Check the status, not just the YAML
`k describe httproute` shows conditions per parent Gateway:
- `Accepted: False` means the route did not attach (wrong Gateway name, wrong namespace, listener does not allow it).
- `ResolvedRefs: False` means a backend Service or port is wrong.

## Exam angle
- Gateway API is in the CKA curriculum since 2025. Expect to write an HTTPRoute from the docs.
- There is no `kubectl create httproute`. Copy from the docs and edit.
- `k get gateway` shows the address and whether it is Programmed.

Bookmark: https://kubernetes.io/docs/concepts/services-networking/gateway/

Your notes: Gateway API
