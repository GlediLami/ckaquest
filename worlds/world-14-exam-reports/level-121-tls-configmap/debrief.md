# Old Clients Need TLS 1.2

## What happened
Changing a ConfigMap does not change a running app on its own.
- Mounted as a whole volume: the file updates after up to a minute, but the app must reload it. nginx does not.
- Mounted with `subPath`, or used as env: never updates. The pod must restart.

`kubectl rollout restart` rolls new pods with the same spec. They read the new config at start.

## Immutable ConfigMaps
`immutable: true` blocks every change to `data`. The kubelet stops watching it, which saves API load in big clusters. To change it later, delete and recreate it, or create a new name and point the Deployment at it.

## Exam angle
- Reported: "add TLS 1.2 next to 1.3 in a ConfigMap, restart the Deployment, test with the given URL".
- Test with `curl --tls-max 1.2`. Without it, curl picks 1.3 and the test proves nothing.

Bookmark: https://kubernetes.io/docs/concepts/configuration/configmap/

Your notes: ConfigMaps and Secrets
