# Ingress Without a Class

## What happened
A cluster can run several Ingress controllers. Each one only serves Ingresses of its class. Without `ingressClassName`, the Ingress is only picked up if one IngressClass carries `ingressclass.kubernetes.io/is-default-class: "true"`. This cluster has none.

## Exam angle
- `k create ingress NAME --class=nginx --rule="host/path*=svc:port"` writes the class for you.
- `k get ingressclass` first. Use the name from there.
- The old annotation `kubernetes.io/ingress.class` is deprecated. Use the field.

Bookmark: https://kubernetes.io/docs/concepts/services-networking/ingress/

Your notes: Networking, Service Networking
