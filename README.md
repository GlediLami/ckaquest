# CKAQuest

A game for preparing for the CKA exam (Certified Kubernetes Administrator, curriculum v1.37).

Every level breaks something on a real Kubernetes cluster, or asks you to build something the way an exam task would. You fix it in a terminal with `kubectl`, `ssh` and `vim`. Then the game checks your work and gives you points.

The goal is to be ready for the exam. You play the levels while you work through a CKA course and the Kubernetes docs. When the exam simulator is done, you also test yourself under exam conditions: a 2-hour timer, weighted tasks, and no hints.

## Status

Work in progress.

| Part | State |
|---|---|
| Worlds 1 to 6: basics, deployments, networking, storage, security, cluster troubleshooting (60 levels) | Playable, tested |
| Worlds 7 to 12: admin and security, Gateway API, Helm and Kustomize, workloads, cluster lifecycle, speed drills (50 levels) | Written, being tested |
| Mock exams: 6 fixed sets (A to F) plus random sets | Written, being tested |
| Offline pack | Written. The full offline proof run is still to do. |

The full plan is in [docs/PLAN.md](docs/PLAN.md).

## What you need

Linux, WSL2 or macOS. Windows only through WSL2.

- Docker (Docker Desktop on macOS and WSL2, Docker Engine on Linux)
- [kind](https://kind.sigs.k8s.io/) **0.33 or newer**. Older versions cannot run the v1.37 node image.
- kubectl, helm, jq, openssl
- Python 3.9 or newer
- About 3 GB of free RAM for the cluster

## Install

```bash
git clone https://github.com/GlediLami/ckaquest.git
cd ckaquest
./install.sh
```

This creates a Python venv and a kind cluster called `ckaquest`: one control plane and two workers, Kubernetes v1.37.0. It also installs metrics-server, the Gateway API CRDs and the VPA CRDs. It puts vim, shell completion and etcdctl on the nodes.

The cluster has its own kubeconfig in `~/.ckaquest/kubeconfig`. Your `~/.kube/config` and your other clusters are not touched.

## Play

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

## Cluster commands

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

## Worlds

| World | Topics | CKA domain |
|---|---|---|
| 1 Basics | CrashLoopBackOff, image pulls, Pending pods, labels, ports, init containers, logs | Workloads, Troubleshooting |
| 2 Deployments | Rollback, probes, HPA, rollouts, PDB, blue/green, canary, StatefulSet | Workloads |
| 3 Networking | Selectors, NodePort, DNS, Ingress, NetworkPolicy, endpoints, headless services | Services and Networking |
| 4 Storage | PVC Pending, mounts, access modes, StorageClass, ConfigMaps, Secrets, reclaim policy | Storage |
| 5 Security | RBAC, securityContext, ResourceQuota, affinity, taints, Pod Security, PriorityClass | Workloads, Architecture |
| 6 Cluster troubleshooting | kubelet down or misconfigured, scheduler, API server, controller manager, CoreDNS, kube-proxy, `kubectl top` and in-place resize, drain with a PDB, static pods | Troubleshooting (30% of the exam) |
| 7 Cluster admin and security | CSR for a new user, ClusterRole, ServiceAccount 403, certificate renewal, etcd backup and restore, kubeconfig repair, static pods, admission plugins, join tokens | Architecture |
| 8 Networking 2 | Gateway API: HTTPRoute, broken routes, 80/20 split, HTTPS listener, migrating from Ingress. IngressClass, cross-namespace NetworkPolicy, CoreDNS hosts | Services and Networking |
| 9 Packaging | Helm install, rollback, finding releases, helm template. Kustomize overlays and patches. CRDs and operator RBAC | Architecture |
| 10 Workloads 2 | Native sidecars, multi-container pods, HPA behavior, VPA, DaemonSets, CronJobs, Secret volumes, default StorageClass, LimitRange, parallel Jobs | Workloads, Storage |
| 11 Cluster lifecycle | Node prep, `kubeadm init`, Calico with a custom CIDR, `kubeadm join`, control plane and worker upgrade to v1.37.1 | Architecture |
| 12 Speed drills | JSONPath, custom-columns, sort-by, imperative commands, `$do`, field selectors, api-resources | All |

## Score, par time and readiness

- Every level has a par time. Clear it in time without the guide or the solution and you get a star and 20% more XP.
- Hints cost XP: 15% each, the guide 25%, the solution 50%.
- The welcome screen shows a mastery bar for each CKA domain and a **readiness** score. Readiness is half campaign mastery (weighted like the exam) and half your last three mock exams. Book the exam when it stays above 80%.
- "Play by course section" in the menu plays the levels that match a section of the course you are watching.

## Mock exams

```bash
./exam.sh list            # sets A to F, plus random
./exam.sh start A         # sets up 17 tasks, then the 2-hour timer starts
./exam.sh                 # task list, weights, time left
./exam.sh task 3          # one task
./exam.sh flag 3          # mark for review
./exam.sh grade           # score per task and per domain, pass mark 66%
./exam.sh review          # solutions, after grading
./exam.sh end             # clean everything up
./exam.sh history
```

Like the real exam there are two clusters. `cluster1` is the game cluster and `cluster2` is the small lab cluster. Each task starts with the `kubectl config use-context` line to run. `ssh cluster1-node01` or `ssh cluster2-controlplane` work like in the exam. There are no hints during a mock.

Upgrade tasks use cluster2. It is created when a set needs it (about 1 GB more RAM).

## Offline

Run this once while online:

```bash
bin/cq-offline prepare    # images, add-on manifests, Calico, the v1.37.1 .debs
```

After that, new clusters load the images from the pack and add-ons come from local files. Upgrade levels install from a local apt repo with the same commands. The docs stay online, as in the real exam. `tests/offline-check.sh` builds a cluster on a Docker network with no internet and runs a few levels to prove it.

## Tests

Every level has a reference fix. The harness deploys each level, checks that the broken state fails, applies the fix, and checks that it passes:

```bash
tests/run-levels.sh world-6      # one world
tests/run-levels.sh level-53     # one level
```

A full run takes a while. Run it in the background.

## Writing a level

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

Apache-2.0, see [License](License). Based on K8sQuest by Manoj ([Manoj-engineer/k8squest](https://github.com/Manoj-engineer/k8squest)).
