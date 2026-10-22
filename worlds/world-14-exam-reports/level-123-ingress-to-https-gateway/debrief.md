# Retire the Ingress

## What happened
An Ingress mixes infrastructure and routing in one object. Gateway API splits them:
- **Gateway**: where traffic enters. Listeners, ports, hostnames, TLS. Owned by the platform team.
- **HTTPRoute**: what goes where. Owned by the app team.

The TLS part of the Ingress (`tls.secretName`) moves to the Gateway listener (`tls.certificateRefs`). Rules move to the HTTPRoute.

## Mapping
| Ingress | Gateway API |
|---|---|
| `ingressClassName` | `gatewayClassName` |
| `tls.hosts`, `secretName` | listener `hostname`, `tls.certificateRefs` |
| `rules.host` | HTTPRoute `hostnames` |
| `pathType: Prefix` | `path.type: PathPrefix` |
| `backend.service` | `backendRefs` |

## Exam angle
- Reported: "migrate an Ingress to Gateway API, Gateway on 443 with TLS, same rules, delete the Ingress".
- Check `k get gateway` shows PROGRAMMED True and the HTTPRoute is Accepted before you move on.

Bookmark: https://gateway-api.sigs.k8s.io/guides/migrating-from-ingress/

Your notes: Gateway API
