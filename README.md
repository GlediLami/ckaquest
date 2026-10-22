# ⚔️ CKAQuest

```
   ██████╗██╗  ██╗ █████╗  ██████╗ ██╗   ██╗███████╗███████╗████████╗
  ██╔════╝██║ ██╔╝██╔══██╗██╔═══██╗██║   ██║██╔════╝██╔════╝╚══██╔══╝
  ██║     █████╔╝ ███████║██║   ██║██║   ██║█████╗  ███████╗   ██║
  ██║     ██╔═██╗ ██╔══██║██║▄▄ ██║██║   ██║██╔══╝  ╚════██║   ██║
  ╚██████╗██║  ██╗██║  ██║╚██████╔╝╚██████╔╝███████╗███████║   ██║
   ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚══▀▀═╝  ╚═════╝ ╚══════╝╚══════╝   ╚═╝
```

**A game that gets you through the CKA exam.** 133 levels, 15 worlds, 10 mock exams, one real Kubernetes v1.37 cluster.

Every level breaks something on the cluster, or hands you a task the way the exam would. You fix it in a real terminal with `kubectl`, `ssh` and `vim`. The game checks your work, gives you XP, and tells you what the exam likes to ask about it.

No multiple choice. No fake shell. If you can clear the game, you can do the exam.

## 🎮 How a level plays

```
╭──────────────── 🎯 MISSION BRIEFING ────────────────╮
│ Level 54: The API Server Is Gone                     │
│ 350 XP · advanced · par 15m · Troubleshooting (30%)  │
│                                                      │
│ After a change on the control plane, kubectl fails   │
│ with connection refused. Find the problem on node    │
│ controlplane and fix it.                             │
│ You cannot use kubectl to debug this one.            │
╰──────────────────────────────────────────────────────╯
> validate
  ✅ API server answers
  ❌ apiserver talks to etcd on the client port 2379
  ✅ kube-apiserver pod is Ready
  ✅ all nodes Ready
  SCORE 4/5
```

1. Read the mission. It names the CKA domain and the doc pages you may open in the exam.
2. Fix it in your second terminal, the "exam terminal".
3. `validate` until every line is green.
4. Read the debrief: what broke, why, and the exam angle.

## 🏆 XP, stars and readiness

| | |
|---|---|
| ⭐ **Star** | Clear a level within par time without the guide or the solution: +20% XP |
| 💡 **Hints** | 3 per level. Each costs 15% of the level XP. The guide costs 25%, the solution 50%. |
| 🔥 **Streak** | Play on consecutive days to keep it going |
| 📊 **Mastery** | One bar per CKA domain, weighted like the exam |
| 🎯 **Readiness** | Half campaign mastery, half your last 3 mock exams. Book the exam when it stays above 80%. |

## 🗺️ The worlds

| World | Levels | You fight | CKA domain |
|---|---|---|---|
| 🌱 1 Basics | 1–10 | CrashLoopBackOff, image pulls, Pending pods, labels, ports, init containers, logs | Workloads, Troubleshooting |
| 🚀 2 Deployments | 11–20 | Rollback, probes, HPA, rollouts, PDB, blue/green, canary, StatefulSet | Workloads |
| 🌐 3 Networking | 21–30 | Selectors, NodePort, DNS, Ingress, NetworkPolicy, endpoints, headless services | Services and Networking |
| 💾 4 Storage | 31–40 | PVC Pending, mounts, access modes, StorageClass, ConfigMaps, Secrets, reclaim policy | Storage |
| 🛡️ 5 Security | 41–50 | RBAC, securityContext, ResourceQuota, affinity, taints, Pod Security, PriorityClass. Ends with the chaos finale. | Workloads, Architecture |
| 🔥 6 Cluster on fire | 51–60 | kubelet down, scheduler, API server, controller manager, CoreDNS, kube-proxy, `kubectl top`, drain with a PDB, hidden static pods | Troubleshooting (30%) |
| 🔐 7 Admin and security | 61–70 | CSR for a new user, ClusterRole, ServiceAccount 403, cert renewal, etcd backup and restore, kubeconfig repair, admission plugins, join tokens | Architecture |
| 🚪 8 Networking 2 | 71–78 | Gateway API: HTTPRoute, broken routes, 80/20 split, HTTPS listener, Ingress migration. IngressClass, cross-namespace NetworkPolicy, CoreDNS hosts | Services and Networking |
| 📦 9 Packaging | 79–86 | Helm install, rollback, find a release, helm template. Kustomize overlays and patches. CRDs and operator RBAC | Architecture |
| ⚙️ 10 Workloads 2 | 87–96 | Native sidecars, multi-container pods, HPA behavior, VPA, DaemonSets, CronJobs, Secret volumes, default StorageClass, LimitRange, parallel Jobs | Workloads, Storage |
| 🏗️ 11 Cluster lifecycle | 97–102 | Node prep, `kubeadm init`, Calico with a custom CIDR, `kubeadm join`, control plane and worker upgrade to v1.37.1 | Architecture |
| ⏱️ 12 Speed drills | 103–110 | JSONPath, custom-columns, sort-by, imperative commands, `$do`, field selectors, api-resources | All |
| 🧩 13 Loose ends | 111–116 | HA control plane join, cri-dockerd from a .deb, pod anti-affinity, topology spread, PVC expansion, CRI/CNI/CSI inspection | Architecture, Workloads, Storage |
| 📰 14 Exam reports | 117–128 | Tasks people report from the 2025/2026 exam: Argo CD chart without CRDs, Calico with the Tigera operator, PVC for a given PV, splitting node resources, TLS config in a ConfigMap, cert-manager CRDs, Ingress to HTTPS Gateway, PriorityClass with patch, sidecar on a Deployment, WaitForFirstConsumer by hand, Ingress TLS, local chart | All |
| 🔎 15 Last gaps | 129–133 | `kubectl debug` (ephemeral and node), the least permissive NetworkPolicy, aggregated ClusterRoles, a Service with a hand-made EndpointSlice, HPA on CPU and memory | All |

Worlds 6 and 11 break or build real control planes. The game repairs the cluster when you finish, skip or reset the level.

## 👹 Boss fight: the mock exam

17 tasks. 2 hours. Two clusters. No hints. Pass mark 66%, like the real thing.

```bash
./exam.sh start A         # sets A to J, or "random"
```

Commands are below in [Mock exams](#mock-exams).

## Status

| Part | State |
|---|---|
| Worlds 1 to 15 (133 levels) | ✅ Playable. Every level passes the test harness. |
| Mock exams: 10 fixed sets (A to J) plus random sets | ✅ Playable |
| Offline pack | ✅ Works. `tests/offline-check.sh` passes sample levels with the internet cut |

The full plan is in [docs/PLAN.md](docs/PLAN.md).

## 🧰 What you need

Linux, WSL2 or macOS. Windows only through WSL2.

- Docker (Docker Desktop on macOS and WSL2, Docker Engine on Linux)
- [kind](https://kind.sigs.k8s.io/) **0.33 or newer**. Older versions cannot run the v1.37 node image.
- kubectl, helm, jq, openssl
- Python 3.9 or newer
- About 3 GB of free RAM for the cluster

## 📥 Install

```bash
git clone https://github.com/GlediLami/ckaquest.git
cd ckaquest
./install.sh
```

This creates a Python venv and a kind cluster called `ckaquest`: one control plane and two workers, Kubernetes v1.37.0. It also installs metrics-server, the Gateway API CRDs and the VPA CRDs. It puts vim, shell completion and etcdctl on the nodes.

The cluster has its own kubeconfig in `~/.ckaquest/kubeconfig`. Your `~/.kube/config` and your other clusters are not touched.

## ▶️ Play

You need two terminals.

**Terminal 1** runs the game:

```bash
./play.sh
```

**Terminal 2** is where you work, like the exam terminal:

```bash
source ./env.sh
```

After that, this terminal talks only to the CKAQuest cluster. You get:

- `k` as an alias for `kubectl`, with completion
- `$do` for `--dry-run=client -o yaml` and `$now` for `--force --grace-period 0`
- `ssh controlplane`, `ssh node01` and `ssh node02` to log into the nodes
- `~/ckaquest-work/` for files that tasks ask you to write

In the exam you log into nodes as a normal user and need `sudo` for root work. To practise that, set `export CQ_NODE_USER=candidate` before `source ./env.sh`. Then `ssh node01` logs in as `candidate`, and editing `/etc/kubernetes/manifests` or restarting the kubelet needs `sudo`.

In the game, each level shows the task, the CKA domain it belongs to and the doc pages you may open in the exam. Commands inside a level:

| Command | What it does |
|---|---|
| `validate` | Checks your work, one line per check, with a score |
| `task` | Shows the task again |
| `check` | Watches the level's namespace for 10 seconds |
| `hints` | Unlocks the next hint (3 per level) |
| `guide` | Step-by-step help |
| `solution` | The reference solution |
| `reset` | Restores the cluster and starts the level again |
| `skip`, `quit` | Skip the level, or save and exit |

After you clear a level you get a debrief: what went wrong, why, and what the exam likes to ask about it.

Some levels break the cluster itself, for example the kubelet or the API server. The game repairs this when you finish, skip or reset the level. If you quit in the middle, it repairs it before the next level starts.

## 🖥️ Cluster commands

```bash
bin/cq-cluster status     # nodes and add-ons
bin/cq-cluster rebuild    # delete and recreate the cluster, if something is really broken
bin/cq-cluster down       # delete the cluster
bin/cq-cluster lab-up     # small 2-node cluster one version behind, for upgrade practice
bin/cq-cluster bare-up    # 2 bare nodes with no cluster yet, for kubeadm init and join practice
bin/cq-cluster addon gateway   # NGINX Gateway Fabric (installed automatically by the levels that need it)
docker stop ckaquest-control-plane ckaquest-worker ckaquest-worker2   # pause it and free RAM
docker start ckaquest-control-plane ckaquest-worker ckaquest-worker2  # resume
```

## Mock exams

```bash
./exam.sh list            # sets A to J, plus random
./exam.sh start A         # sets up 17 tasks, then the 2-hour timer starts
./exam.sh                 # task list, weights, time left
./exam.sh task 3          # one task
./exam.sh flag 3          # mark for review
./exam.sh grade           # score per task and per domain, pass mark 66%
./exam.sh review          # solutions, after grading
./exam.sh end             # clean everything up
./exam.sh history
```

Like the real exam there are several clusters. `cluster1` is the game cluster, `cluster2` the small lab cluster for upgrades, and `cluster3` two bare nodes for install tasks (cri-dockerd, kubeadm init, CNI, HA). Each task starts with the `kubectl config use-context` line to run. `ssh cluster1-node01` or `ssh cluster2-controlplane` work like in the exam. There are no hints during a mock.

cluster2 and cluster3 are only created when a set needs them (about 1 GB more RAM each). Sets G to J each have one install task on cluster3, and every exam task appears in at least one set.

## ✈️ Offline

Run this once while online:

```bash
bin/cq-offline prepare    # images, add-on manifests, Calico, the v1.37.1 .debs
```

After that, new clusters load the images from the pack and add-ons come from local files. Upgrade levels install from a local apt repo with the same commands. The docs stay online, as in the real exam. `tests/offline-check.sh` builds a separate cluster, cuts the internet inside every node, loads the pack and runs a few levels to prove it.

## 🧪 Tests

Every level has a reference fix. The harness deploys each level, checks that the broken state fails, applies the fix, and checks that it passes:

```bash
tests/run-levels.sh world-6      # one world
tests/run-levels.sh level-53     # one level
```

A full run takes a while. Run it in the background.

## ✍️ Writing a level

A level is a folder in `worlds/world-N-name/level-NN-name/`:

| File | Purpose |
|---|---|
| `mission.yaml` | Name, task text, CKA domain, namespace, doc links, XP |
| `setup.sh` | Optional. Prepares the scenario, for example by breaking a node. |
| `broken.yaml` | Optional. Applied after `setup.sh`. |
| `validate.sh` | Checks the result with `lib/validate.sh` |
| `solve.sh` or `solution.yaml` | Reference fix, used by the tests |
| `cleanup.sh` | Optional. Undoes changes outside the namespace. |
| `hint-1.txt` to `hint-3.txt`, `solution.md`, `debrief.md` | Learning content |

## License

Apache-2.0, see [License](License).
