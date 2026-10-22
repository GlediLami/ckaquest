# Lock the Front Door

## What happened
An Ingress terminates TLS when `spec.tls` lists the hosts and a Secret of type `kubernetes.io/tls`. The controller loads the certificate and serves HTTPS for those hosts. Traffic to the Service stays plain HTTP.

## Details
- The Secret must be in the same namespace as the Ingress.
- `tls.hosts` must match `rules.host`, or the controller serves its default certificate.
- ingress-nginx redirects HTTP to HTTPS for TLS hosts by default.

## Exam angle
- `k create ingress ... --rule="host/path=svc:port,tls=secret"` writes the whole thing in one line.
- Test with `curl -k --resolve host:443:<ip>`. Without the right Host or SNI you get the default backend.

Bookmark: https://kubernetes.io/docs/concepts/services-networking/ingress/#tls

Your notes: Ingress
