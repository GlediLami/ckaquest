# Coverage gaps (2026-10-22)

**Status (2026-10-22):** all closed except G14. World 14 (117 to 128) closes G1, G3, G4, G6, G7, G8, G11, G13, G15, G16. Level 92 covers G17. World 15 (129 to 133) closes G2, G5, G9, G10, G12. Install tasks now run in mocks on cluster3, and sets G to J put every exam task in at least one set (97, 99 and 100 only in random sets, one install task per set). G14 (kubelet to cri-dockerd) stays open: it needs a real Docker Engine inside the node. `sudo` login: `CQ_NODE_USER=candidate`.

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

## 4. theplatformlab mock exams (2 x 15 questions, "Kubernetes 1.35")

Source: github.com/theplatformlab/CKA-Certified-Kubernetes-Administrator, `mock-exams/`. Its exercises 18 to 31 match the April 2026 exam report (cri-dockerd, Tigera, Argo CD, TLS config, PriorityClass patch, WaitForFirstConsumer, resource tuning, etcd endpoint).

| Mock 1 | Ours | | Mock 2 | Ours | |
|---|---|---|---|---|---|
| 1 ConfigMap as a file for a crashing pod | 36, 93 | ✅ | 1 Cross-namespace DNS | 23, 27 | ✅ |
| 2 Role + RoleBinding, `auth can-i` | 41, 61 | ✅ | 2 Rollout history, rollback | 11 | ✅ |
| 3 Drain for maintenance | 59 | ✅ | 3 Secret as env vars | 37, 93 | ✅ |
| 4 SC + PV + PVC (RWX) + mount in a Deployment | 31, 33, 35 | 🟡 G11 | 4 DaemonSet on control plane too | 91 | ✅ |
| 5 Three-tier NetworkPolicies with ports | 25, 44, 77 | ✅ | 5 API server debugging | 54 | ✅ |
| 6 Local chart dir, `--set`, `--create-namespace` | 79, 82 | 🟡 G16 | 6 ConfigMap changes reach pods (volume vs env vs subPath) | 36 | 🟡 G15 |
| 7 Point the kubelet at cri-dockerd | 112 installs only | 🟡 G14 | 7 PriorityClass preemption | 49 | ✅ |
| 8 API server audit logs | none | ⚪ CKS topic, not in the CKA curriculum | 8 NodePort / LoadBalancer | 22, 29 | ✅ |
| 9 HPA 70% CPU | 14 | ✅ | 9 CronJob schedule, history, `suspend` | 92 | 🟡 suspend missing |
| 10 Ingress with TLS | none (74 is Gateway TLS) | ❌ G13 | 10 kubeadm cert renewal | 64 | ✅ |
| 11 Scheduler down | 53 | ✅ | 11 PDB + drain | 16, 47, 59 | ✅ |
| 12 StatefulSet + headless + volumeClaimTemplates | 19, 30, 34 | ✅ | 12 CRD instance | 85 | ✅ |
| 13 ResourceQuota + LimitRange | 43, 95 | ✅ | 13 PSS enforce + warn | 48 | ✅ |
| 14 PSS enforce restricted, audit baseline | 48 | ✅ | 14 Dynamic provisioning | 35, 94 | ✅ |
| 15 Sidecar tails nginx logs | 7, 87 | ✅ | 15 Quota + LimitRange min/max | 43, 95 | ✅ |

Result: 22 ✅, 6 🟡, 1 ❌, 1 out of scope.

New gaps from it:

| # | Topic |
|---|---|
| G13 | Ingress with a `tls:` section and a TLS Secret |
| G14 | Switch the kubelet to cri-dockerd (`containerRuntimeEndpoint`, `--cri-socket`) |
| G15 | How ConfigMap changes reach pods: mounted volume updates, env and `subPath` do not, `rollout restart` |
| G16 | Install a chart from a local directory with `--set` and `--create-namespace` |
| G17 | CronJob `suspend` |

## 5. Official curriculum v1.37 (cncf/curriculum, current)

| Domain | Curriculum item | Levels |
|---|---|---|
| Storage 10% | Storage classes and dynamic provisioning | 35, 94, 115 |
| | Volume types, access modes, reclaim policies | 32, 33, 38, 39, 40 |
| | PVs and PVCs | 31, 34, 105 |
| Troubleshooting 30% | Clusters and nodes | 51, 52, 59, 67 |
| | Cluster components | 53 to 57, 60 |
| | Resource usage monitoring | 14, 58 |
| | Container output streams | 1, 8, 54 |
| | Services and networking | 21, 23, 28, 72 |
| Workloads 15% | Deployments, rolling update, rollback | 2, 11, 15, 17, 18 |
| | ConfigMaps and Secrets | 36, 37, 93 |
| | Workload autoscaling | 14, 89, 90 |
| | Self-healing primitives | 12, 13, 19, 20, 91, 92, 96 |
| | Pod admission and scheduling | 4, 43, 45 to 49, 95, 113, 114 |
| Architecture 25% | RBAC | 41, 61, 62, 63, 86 |
| | Prepare infrastructure | 97, 112 |
| | Clusters with kubeadm | 70, 98, 100 |
| | Cluster lifecycle | 64, 65, 66, 101, 102 |
| | HA control plane | 111 |
| | Helm and Kustomize | 79 to 84 |
| | Extension interfaces (CNI, CSI, CRI) | 99, 112, 116 |
| | CRDs and operators | 85, 86 |
| Networking 20% | Pod connectivity | 5, 6, 27 |
| | NetworkPolicies | 25, 44, 77 |
| | ClusterIP, NodePort, LoadBalancer, endpoints | 21, 22, 26, 29, 30 |
| | Gateway API | 71 to 74, 76 |
| | Ingress controllers and resources | 24, 75 |
| | CoreDNS | 23, 56, 78 |

Every curriculum item has at least one level. The thinnest are the HA control plane (1 level) and installing operators (85 and 86 only define a CRD and RBAC. No level installs a real operator, which G1 Argo CD and G8 cert-manager would fix).
