# Migrate to Gateway API

## Mapping
| Ingress | HTTPRoute |
|---|---|
| `ingressClassName` | Gateway `gatewayClassName`, route `parentRefs` |
| `rules[].host` | `hostnames` |
| `paths[].path` + `pathType: Prefix` | `matches[].path` with `type: PathPrefix` |
| `backend.service.name/port.number` | `backendRefs[].name/port` |
| `tls` | Gateway listener with `tls` |

## Exam angle
- The tool `ingress2gateway` exists, but in the exam you write it by hand.
- Delete the old Ingress only after the route works.

Bookmark: https://gateway-api.sigs.k8s.io/guides/migrating-from-ingress/

Your notes: Gateway API
