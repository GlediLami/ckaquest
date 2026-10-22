# Coverage gaps (2026-10-22)

Compared: the 116 levels and mock sets A to F, against the official CKA curriculum, the 40 questions of the 3 KodeKloud mock exams in the course notes, and topic-level reports of the 2025/2026 exam (study repos and blogs). Real exam questions are under NDA, so only topics are used.

## 1. Topics no level covers

| # | Topic | Seen in | Why it matters |
|---|---|---|---|
| G1 | Third-party Helm chart with options: add repo, pick a version, turn off CRD install (`--set crds.install=false`), `helm template` to a file. The reported example is Argo CD. | exam reports | We have helm install, rollback and template (79 to 82), but never a chart flag that skips CRDs or output to a given file |
| G2 | `kubectl debug`: ephemeral container in a running pod, debug copy of a pod, `kubectl debug node/...` | exam reports, curriculum troubleshooting | Not in any level |
| G3 | App TLS config in a ConfigMap (for example nginx `ssl_protocols TLSv1.3` only), make the ConfigMap `immutable`, roll the Deployment, verify with `curl --tls-max` | exam reports | ConfigMaps are covered, immutable and app config change are not |
| G4 | Split node resources evenly: read node allocatable, set requests and limits so N replicas (plus init containers) fit | exam reports | 4 and 95 touch requests, none makes you calculate from allocatable |
| G5 | Pick the least permissive NetworkPolicy from several given files and apply only that one | exam reports | 25, 44, 77 have you write policies, not compare them |
| G6 | Calico through the Tigera operator (`tigera-operator.yaml`, `custom-resources.yaml` with the pod CIDR). Choosing a CNI that supports NetworkPolicy (Calico, not Flannel) | exam reports, KodeKloud mock 2 Q14 | 99 uses the plain Calico manifest only |
| G7 | Gateway API beyond the basics: create the Gateway yourself (listeners, `allowedRoutes` from other namespaces), header matches, filters (`RequestRedirect` HTTP to HTTPS, `RequestHeaderModifier`), `ReferenceGrant` | exam reports | 71 to 76 always give you a ready Gateway |
| G8 | Read docs of an installed operator CRD: list its CRDs to a file, `kubectl explain <kind>.spec.<field>` to a file (cert-manager style) | exam reports, KodeKloud mock 1 Q3 | 85 creates a CRD, 110 is api-resources. Neither works with an installed operator |
| G9 | Aggregated ClusterRoles (`aggregationRule`, `rbac.authorization.k8s.io/aggregate-to-*` labels) | reports | RBAC levels 41, 61 to 63, 86 never aggregate |
| G10 | Service without selector plus a manual EndpointSlice (external backend) | curriculum "service types and endpoints" | Endpoints only show up in troubleshooting |
| G11 | Bind a PVC to one specific retained PV (`volumeName`, `storageClassName: ""`), then point a Deployment at it (the "restore the database volume" shape) | exam reports, KodeKloud mock 3 Q8 | 31 and 39 come close, but no level binds to a named PV |
| G12 | HPA on a custom or Pods metric, not only CPU | KodeKloud mock 3 Q11 | 14 and 89 are CPU only |

## 2. Covered, but never in a mock

The fixed sets were built before World 13 and leave out the bare node levels. So a mock never trains:

- **Install tasks**: cri-dockerd (112), node prep sysctls (97), CNI install (99), kubeadm init and join (98, 100), HA endpoint (111). These are reported as real exam tasks. Mocks only have the upgrade tasks (101, 102) on cluster2.
- **Architecture classics**: cert renewal (64), etcd restore (66), static pod (68), admission plugins (69), RBAC user (41), Pod Security (48)
- **Workloads**: rollback (11), probes (12, 13), HPA (14), rolling update strategy (15)
- **World 13**: anti-affinity (113), topology spread (114), PVC expansion (115), CRI/CNI/CSI (116)

36 exam-eligible levels never appear in sets A to F. The random set can draw them.

## 3. Suggested fixes

1. World 14 with 8 levels for G1, G2, G3, G4, G5, G7, G8, G11. Each is a short exam-shaped task.
2. Add G6 (Tigera operator) as a variant of level 99, and G9, G10, G12 as single levels.
3. Make install tasks possible in mocks: bring up the bare nodes as `cluster3` when a set needs them, like `cluster2` for upgrades.
4. Rebuild sets A to F so that every exam-eligible level appears in at least one set. Add sets G and H for the rest.
