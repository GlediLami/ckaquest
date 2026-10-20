# CKAQuest Plan

Goal: pass the CKA (curriculum v1.37). Get as close to the real exam as possible.

Two ways to use CKAQuest:

1. **Campaign.** A game like K8sQuest. You play levels while you watch the course and read the docs. It has hints, debriefs and XP. You learn here.
2. **Exam simulator.** Like killer.sh, but local and 100% offline. 2 hours, about 17 weighted tasks, several clusters, no hints, a score at the end. You test yourself here.

Status: on 2026-10-20 work stopped after World 6 was written. This file is the plan for everything after that.

## 1. Where we are

| Part | State |
|---|---|
| Repo `~/projects/ckaquest`, Apache-2.0, base imported from K8sQuest | Done, 2 commits, local only |
| Own kind cluster `ckaquest`, 3 nodes, v1.37.0, own kubeconfig `~/.ckaquest/kubeconfig` | Done. Other clusters and `~/.kube/config` stay untouched. |
| `env.sh` exam shell: `k`, `$do`, `$now`, completion, `ssh node01` | Done |
| Node tools: vim, completion, kubectl, etcdctl/etcdutl 3.7.0 | Done, not committed |
| Engine: auto worlds, task panel, domain, docs links, setup/cleanup, reset | Done |
| `lib/validate.sh` partial scoring, `tests/run-levels.sh` harness | Done |
| Base 50 levels on the new cluster | Harness run in progress (see section 9) |
| World 6 Cluster Troubleshooting, levels 51 to 60 | Written, not tested, not committed |
| Worlds 7 to 10, exam simulator, offline mode | Not started |

## 2. Sources

What we use, and how. We write all content ourselves. Sources only give topics and ideas.

| Source | What it has | License | How we use it |
|---|---|---|---|
| [CNCF CKA curriculum v1.37](https://github.com/cncf/curriculum) | Official domains and weights | public | The coverage matrix (section 7) follows it bullet by bullet |
| KodeKloud CKA course mock exams 1 to 3 (owned course copy, not in repo) | 40 exam-style questions | paid course content | Topics and style only. Every task is reworded with new names. |
| Your vault `k8s-notes` | Notes per topic, course checklists 01 to 15 | yours | Debriefs link to note names. Levels are tagged with course sections. |
| [ViktorUJ/cks](https://github.com/ViktorUJ/cks) | 35 CKA labs (101 to 125 follow the curriculum), 2 CKA mock exams with weights and acceptance criteria | Apache-2.0 | **Topic checklist only.** We read their lab list to find gaps. We write every task, script and check ourselves. |
| [sailor-sh/CK-X](https://github.com/sailor-sh/CK-X) | Local exam simulator (web UI, k3d), 2 CKA exams with setup and validation scripts | Business Source License 1.1. Personal and educational use is allowed. | **Used as a second simulator, installed separately** (section 4.4). Not vendored, no code or questions copied into our repo. |
| [techiescamp/cka-certification-guide](https://github.com/techiescamp/cka-certification-guide) | Study guide for v1.35 | no license | Reading list only |
| [chadmcrowell/CKA-Exercises](https://github.com/chadmcrowell/CKA-Exercises) | Exercises by the author of "Acing the CKA" | no license | Ideas only |
| [alijahnas/CKA-practice-exercises](https://github.com/alijahnas/CKA-practice-exercises) | Exercises, last update 2024 | GPL-3.0 | Skip. Outdated, and GPL would bind our repo. |
| killer.sh | Official simulator, 2 sessions with the exam purchase | paid | Use your 2 sessions in the last week. Harder than the real exam. |
| Killercoda | Free CKA playground similar to the exam environment | free tier | Optional extra practice. The Killer Shell CKA scenario page says "moved". |
| [Sailor.sh: practice CKA for free](https://www.sailor.sh/blog/how-to-practice-cka-for-free), [DevOpsCube course list](https://devopscube.com/best-cka-courses/), [ExamCert free practice](https://www.examcert.app/blog/free-cka-practice-test-2026/) | Overviews of free resources | blogs | Used to find the sources above |
| KodeKloud community exam reports | Candidate reports: Gateway API, Helm, CRD, HPA, PriorityClass, NetworkPolicy, StorageClass | forum | Confirms which topics show up in real exams |

Rule: **we write everything ourselves.** Outside sources give topics and ideas only. No task text, scripts, YAML or solutions are copied from any of them. So no attribution is owed to anyone except the K8sQuest base (section 11). A thank-you list of resources goes in the README as a courtesy.

## 3. Campaign (the game)

### 3.1 World layout

| World | Theme | Levels | State |
|---|---|---|---|
| 1 to 5 | K8sQuest base: pods, deployments, networking, storage, security | 50 | Exists. Gets the upgrades in 3.3. |
| 6 | Cluster troubleshooting: kubelet, static pods, API server, controller manager, CoreDNS, kube-proxy, top, drain, mirror pods | 51 to 60 | Written |
| 7 | Cluster admin and security: CSR user, ClusterRole, SA 403, cert renew, etcd backup, etcd restore, kubeconfig repair, static pod create, admission plugin | 61 to 70 | Designed |
| 8 | Networking 2025: Gateway + HTTPRoute, HTTPS listener, 80/20 split, Ingress with class, NetworkPolicy across namespaces, CoreDNS custom config | 71 to 78 | Designed |
| 9 | Packaging and extensions: Helm install/upgrade/rollback/find release, Kustomize overlay and patches, CRD + CR, operator RBAC | 79 to 86 | Designed |
| 10 | Workloads, autoscaling, storage: native sidecar, 3-container pod, HPA with behavior, VPA, DaemonSet on all nodes, CronJob, ConfigMap/Secret, StorageClass default, PriorityClass | 87 to 96 | Designed |
| 11 | Lifecycle on the lab cluster: node prep (sysctl, modules), kubeadm init and join, CNI install (Calico, custom CIDR), kubeadm upgrade control plane, upgrade worker, HA concepts | 97 to 102 | Needs a feasibility test (section 8) |
| 12 | Speed drills: JSONPath, custom-columns, imperative commands, `$do` YAML, against a clock | 103 to 110 | Own drills |

About 110 levels in total. Every curriculum bullet gets at least 2 levels.

### 3.2 Sync with the course

- Every level gets `course_section: <n>` (the Udemy sections 01 to 15 from your vault checklists).
- New menu entry: "Play by course section". After you watch section 9 (Networking), you play the networking levels.
- Every debrief ends with "Your notes:" (vault note names) and the kubernetes.io page to bookmark.

### 3.3 Upgrades for the base 50

1. Done: levels 12, 14 and 37 fixed (2026-10-20).
2. Add `domain`, `task`, `docs`, `course_section` to every `mission.yaml`.
3. Rewrite the loose validators with `lib/validate.sh`. Level 1 example: it passes if the command line is just deleted.
4. Add an "Exam angle" section to each debrief: the fastest imperative command and the doc page.
5. Move each level from the shared `ckaquest` namespace to its own namespace. Then the exam simulator can reuse them.

### 3.4 Game mechanics

- XP only on first clear (done).
- **Par time** per level (exam pace is about 6 minutes per task). Beat it and earn a bonus star.
- **Domain mastery bars** on the welcome screen, one per CKA domain.
- **Readiness score**: campaign mastery plus your last 3 exam simulator results. The goal is above 80% before you book.
- **Streak**: days in a row with at least one level.
- **Hint cost**: hints lower the XP of that clear, so you only use them when you need them.

## 4. Exam simulator (offline killer.sh)

### 4.1 Feel of the real exam

- `./exam.sh start` sets up all tasks, starts a 120-minute timer and opens the task list.
- **Two clusters** like the real exam: `cluster1` (3 nodes) and `cluster2` (2 nodes, smaller). Each task names its context: `kubectl config use-context cluster1`.
- `ssh cluster1-controlplane`, `ssh cluster2-node01`, as in the exam.
- Results files go to `/opt/course/<n>/` on the right host, like killer.sh.
- Commands: `exam.sh tasks`, `exam.sh task 7`, `exam.sh flag 7`, `exam.sh time`, `exam.sh grade`, `exam.sh review`.
- Grade: per-check points, weighted per task, pass mark 66%, report per domain, saved to history.
- Review: after grading, solutions are unlocked for every task.

### 4.2 Task bank

- Own folder `exam/tasks/<id>/` with `task.md` (text, weight, domain, cluster), `setup.sh`, `check.sh` (partial points), `solution.md`.
- Every task uses its own namespace and names, so 17 tasks can live together.
- Node-breaking tasks are tagged (`breaks: node01`). The set builder never picks two that break the same node.
- Target: about 100 tasks. All written by us: our campaign levels in exam form, plus new tasks for every curriculum topic. Outside sources (ViktorUJ, CK-X, KodeKloud mocks) are only used to check that no topic is missing.

### 4.3 Exam sets

- 6 fixed mocks (A to F), each mirrors the domain weights: about 5 troubleshooting, 4 architecture, 3 or 4 networking, 3 workloads, 2 storage.
- Two levels of difficulty: "real" (like the exam) and "killer" (harder, more steps per task).
- `exam.sh start random` builds a new set from the bank with the same weights.

### 4.4 CK-X as a second simulator (decided)

- CK-X stays a separate install. `bin/cq-ckx` is a small helper: `install` (git clone into `~/.ckaquest/ck-x`, `docker compose up -d`), `start`, `stop`, `open` (http://localhost:30080).
- Our repo only contains this helper and a README section. No CK-X code or questions. That keeps our repo free of the CK-X license (see section 11).
- CK-X needs internet for its first install. After that it runs locally.
- Never run CK-X and our exam mode at the same time (RAM). The helper stops our clusters first.
- Plan: CK-X CKA exams 001 and 002 as extra mocks in the last 2 weeks, between our mocks and killer.sh.

## 5. 100% offline

Everything gets downloaded once while you are online. After that, the clusters, levels and exam need no network. Only the docs are online (decided, like in the real exam).

| Item | How |
|---|---|
| Node image | Build our own `ckaquest-node:v1.37.0` FROM kindest/node. It has vim, completion, etcdctl/etcdutl and cached kubeadm/kubelet/kubectl `.deb` files for v1.37.1 (for the upgrade levels). This replaces the apt step at bootstrap. |
| Container images | `bin/cq-offline prepare` collects every image used by levels, tasks and add-ons, and stores them as one tar. At cluster creation it loads them into the nodes (`kind load image-archive`). A local `registry:2` mirror on the kind network is the backup option. |
| Add-on manifests and charts | Vendored in `cluster/vendor/`: metrics-server, Gateway API CRDs, NGF chart `.tgz`, ingress-nginx, Calico, VPA CRDs |
| Helm repo for levels | Already local (`python3 -m http.server` on 127.0.0.1) |
| Lab cluster upgrade target | The v1.37.1 control plane images and debs are part of the offline pack |
| Docs | **Online docs (decided).** The exam allows kubernetes.io, Helm and Gateway API docs anyway. Every task and debrief links the right page. No offline docs copy. |
| Proof | `tests/offline-check.sh`: cut the network (Docker network without internet), rebuild the clusters, run one full exam set. |

## 6. Hardware limits

Decided: exam mode uses **2 clusters**.

Reference machine: a 16 GB laptop, WSL2 with about 10 GB. Other kind clusters may run at the same time.

| What | RAM (rough) |
|---|---|
| cluster1, 3 nodes, metrics-server | 1.5 to 2 GB |
| cluster2, 2 nodes, no extras | 1 to 1.2 GB |
| Gateway controller + ingress-nginx (only when a task needs them) | 0.5 GB |
| Calico (only CNI tasks, on cluster2) | 1 GB |
| CK-X (8 containers + k3d) | 2 to 3 GB, never together with ours |

Ways to make it fit, in this order:

1. **Only one thing runs at a time.** `exam.sh start` stops other kind clusters with `docker stop` (other games, the campaign nodes) and `exam.sh end` starts them again. Stopped kind clusters keep their state.
2. **Small cluster2**: 1 control plane + 1 worker, no metrics-server.
3. **Add-ons on demand** only for the tasks in the chosen set.
4. **Measure first** (phase 2 spike): `docker stats` during a full mock. Only then decide on more RAM.
5. **If still tight: give WSL 12 GB.** In `%UserProfile%\.wslconfig` set `[wsl2]` `memory=12GB`, then `wsl --shutdown`. That leaves Windows 4 GB, which is fine while you only run a browser and a terminal. Do it only if step 4 shows the need.
- Heavy runs (harness over all levels) are capped with `systemd-run` .
- macOS (work MacBook, arm64): all images must be multi-arch. The offline pack builds per architecture.

## 7. Coverage matrix (curriculum v1.37)

| Curriculum bullet | Campaign levels | Exam bank |
|---|---|---|
| **Storage 10%**: storage classes and dynamic provisioning | 31, 35, 10.x StorageClass default | yes |
| volume types, access modes, reclaim policies | 32, 33, 39, 40 | yes |
| PV and PVC | 31, 34 | yes |
| **Troubleshooting 30%**: clusters and nodes | 51, 52, 59, 60 | yes, high count |
| cluster components | 53, 54, 55, 56, 57 | yes, high count |
| monitor resource usage | 58, 14 | yes |
| container output streams | 8, 7 | yes |
| services and networking | 21 to 28, 56, 57 | yes |
| **Workloads 15%**: deployments, rolling update, rollback | 2, 11, 15, 17, 18 | yes |
| ConfigMaps and Secrets | 36, 37, 10.x | yes |
| workload autoscaling (HPA, VPA) | 14, 10.x | yes |
| self-healing primitives | 12, 13, 20 | yes |
| Pod admission and scheduling (limits, affinity) | 4, 43, 45, 46, 49, 7.x admission plugin | yes |
| **Architecture 25%**: RBAC | 41, 61, 62, 63 | yes |
| prepare infrastructure | 11.x node prep | yes (lab cluster) |
| create and manage clusters with kubeadm | 11.x init/join, 64 certs | yes (lab cluster) |
| cluster lifecycle | 11.x upgrade, 65, 66 etcd | yes |
| HA control plane | 11.x concept level (3 control planes is too heavy for 10 GB) | theory questions only |
| Helm and Kustomize | 9.x | yes |
| extension interfaces (CNI, CSI, CRI) | 11.x CNI install, CRI and CSI inspection tasks | yes |
| CRDs and operators | 9.x | yes |
| **Networking 20%**: pod connectivity | 6, 27, 57 | yes |
| Network Policies | 25, 44, 8.x | yes |
| ClusterIP, NodePort, LoadBalancer, endpoints | 21, 22, 28, 29, 30 | yes |
| Gateway API | 8.x (3 levels) | yes |
| Ingress controllers and resources | 24, 8.x | yes |
| CoreDNS | 23, 56, 8.x | yes |

## 8. Phases

Each phase ends with the harness green for everything in it and a commit.

| # | Phase | Done when |
|---|---|---|
| 1 | Done (2026-10-20): base 50 and World 6 tested, 12, 14, 37, 45 to 50 fixed | Harness shows 60 of 60 OK |
| 2 | Done (2026-10-21), see section 12. Feasibility spikes: kubeadm upgrade inside kind, kubeadm init/join on bare kind node images, Calico in kind, offline image loading, offline docs build | One short report: what works, what gets dropped |
| 3 | Base 50 upgrade (section 3.3) | Every level has task, domain, docs, course section, strict validator |
| 4 | Worlds 7 to 10 | Harness green |
| 5 | Exam simulator engine plus 2 mock sets | You can do a full mock end to end |
| 6 | Offline pack and offline proof | A full mock runs with the network cut |
| 7 | World 11 (lab cluster), World 12 drills, 4 more mock sets, random sets | 6 mocks plus random |
| 8 | Polish: game mechanics (par time, mastery, readiness), security and code review pass | Review findings fixed |

Suggested order of your own study: play worlds 1 to 5 now (they work). Phases 1 to 4 run in parallel with your course sections 1 to 10. Exam mocks are ready before you reach the course mock exams.

## 9. Test results so far

Harness run on the base 50 levels against the new 3-node v1.37 cluster (2026-10-20).

**44 of 50 are clean.** The broken state fails validation and the reference fix passes.

| Level | Result | Cause | Fix (phase 1) |
|---|---|---|---|
| 12 liveness | Broken state already passes | Validator too loose | Rewrite with `lib/validate.sh` |
| 37 secret-encoding | Broken state already passes | Validator too loose | Rewrite with `lib/validate.sh` |
| 14 hpa | No automatic fix | No `solution.yaml` or `solve.sh`. metrics-server is now preinstalled, so the level also needs a new fault. | New fault + `solve.sh` |
| 45 node-affinity | Fix does not pass, pod stays Pending | `setup.sh` labels the first node. With 3 nodes that is the control plane, which has a NoSchedule taint. | Label a worker (node01) |
| 48 pod-security | Setup fails | `broken.yaml` labels the namespace `restricted` and the bad pod is rejected at apply time. The engine treats the rejection as a setup error. | Create the pod first, label the namespace after, or make the rejection part of the task |
| 49 priorityclass | Setup fails | Side effect of 48: the `restricted` label stayed on the shared `ckaquest` namespace | Per-level namespaces (3.3 item 5). Engine resets namespace labels. |

Two lessons for the engine:

- A shared namespace leaks state between levels. Per-level namespaces fix the whole class.
- Any level that picks "the first node" breaks on multi-node. Grep for `items[0]` and use exam node names.

World 6 (levels 51 to 60): 10 of 10 clean.

Update (2026-10-20): 12, 14, 37, 45 to 50 fixed and re-tested. **All 60 levels pass.**

## 10. Decisions (2026-10-20)

| Question | Decision |
|---|---|
| CK-X | Use it as a second simulator, installed separately (4.4) |
| Docs | Online docs, like the real exam |
| Exam clusters | 2 clusters. Fit RAM with section 6. More WSL RAM only if measured. |
| GitHub | Public repo `GlediLami/ckaquest` if the licenses allow it, else private. See section 11. |

## 11. Public repo: license check

Result: **public is possible.** Conditions:

| Content | Can it be public? | Why |
|---|---|---|
| K8sQuest base | Yes | Apache-2.0. Keep the License file, credit the original repo in the README, note that the files were changed. K8sQuest has no NOTICE file, so we do not need one. |
| Outside sources (ViktorUJ, CK-X, KodeKloud, others) | Yes | Nothing copied. Topics and ideas only. Optional thank-you list in the README. |
| CK-X | Yes, because we do not ship it | Only our install helper and a link. The BSL limits using, hosting and selling CK-X itself, not a script that clones it for a user. |
| KodeKloud mock topics | Yes, if reworded | Exam topics are not protected, the text is. Own wording, own names and namespaces, no screenshots, no copied solutions. |
| Your vault references | Make optional | Debriefs say "Your notes: <note name>". In public that is fine, but it is personal. Move the note names into a mapping file you can keep private (`notes-map.yaml`, gitignored, with a public example). |
| Personal paths | Remove | No private home folder paths in the repo. Checked before the first push. |

Before the first push: `git grep` for personal paths and emails, run a secret scan, and check that no task text matches an outside source.

## 12. Phase 2 spikes

Run on the lab cluster and on bare node containers, 2026-10-21. Logs in `~/.ckaquest/spikes/`.

### 12.1 kubeadm upgrade inside kind: works

v1.36.4 to v1.37.1 on a 2-node lab cluster, the exam way: add the pkgs.k8s.io v1.37 apt repo, `apt-get install kubeadm`, `kubeadm upgrade plan`, `kubeadm upgrade apply`, drain, `apt-get install kubelet kubectl`, restart kubelet, uncordon. Worker: `kubeadm upgrade node`, same kubelet steps.

- kind installs the binaries without dpkg, so apt simply replaces them.
- `apt-get install kubelet` stops at a dpkg prompt about kind's `/etc/default/kubelet`. Fix: `--force-confold` in `/etc/apt/apt.conf.d`. Now in `node-bootstrap.sh`.
- `kubeadm upgrade apply` took 3m50s, mostly image pulls. The offline pack must preload the target control plane images.
- Online needs: the apt repo and the images. Offline plan: a local apt repo of the target .debs, served from the host or copied into the node.

### 12.2 kubeadm init and join on bare nodes: works

A bare node is a container from the kindest/node image started without kind (same flags kind uses: privileged, tmpfs /run and /tmp, a /var volume, network `kind`). systemd and containerd run. kubelet waits for a config.

- First try failed: WSL has swap on and kubelet refuses to start. `swapoff` cannot work inside a container. Fix: `KUBELET_EXTRA_ARGS=--fail-swap-on=false` in `/etc/default/kubelet`, set before the player starts. The player still runs plain `kubeadm init --pod-network-cidr=...`.
- With that, `kubeadm init` took 37s. `kubeadm join` works with the printed command.
- `kubeadm reset` on a kind-made cluster is a bad base for levels. Fresh bare containers are cleaner and quicker.

### 12.3 Calico on bare nodes: works, with one hidden fix

`kubectl apply -f calico.yaml` (v3.33.0, pod CIDR 192.168.0.0/16). Nodes go Ready, CoreDNS starts, pods on different nodes ping each other, DNS resolves.

- First try failed: kube-proxy crashes with `open /proc/sys/net/netfilter/nf_conntrack_max: permission denied`. Without kube-proxy the Service IP 10.96.0.1 does not route, so Calico's install step cannot reach the API server.
- kind avoids this with `conntrack.maxPerCore: 0` in the kube-proxy config. A plain `kubeadm init` does not set it.
- Fix, tested end to end with plain exam commands: `cq-cluster bare-up` installs a small systemd unit on the control plane (`cluster/bare-proxy-fix.sh`). After the player's `kubeadm init` it sets `maxPerCore: 0` in the kube-proxy ConfigMap and restarts kube-proxy. The player types the normal exam commands.
- Calico image pulls take about 45s. The offline pack must preload them.

### 12.4 Offline image loading: works

`docker save --platform linux/amd64 IMAGE -o x.tar`, then `ctr -n k8s.io images import --platform linux/amd64 - < x.tar` inside the node. A pod with `imagePullPolicy: Never` runs from it.

- Without `--platform`, Docker 29 saves a multi-platform index and the import fails with `content digest ... not found`.
- On arm64 Macs the platform is linux/arm64. The pack script must pick the host platform.

### 12.5 RAM (WSL, 9.7 GB)

Measured with docker stats, idle:

| Containers | RAM |
|---|---|
| Main cluster (3 nodes) | about 1.2 GB |
| Lab cluster (2 nodes, kindnet) | about 1.0 GB |
| Bare nodes after init plus Calico | about 2.1 GB |

Main cluster plus one of the others fits with 4 GB still free. All three at once is tight. The exam simulator with 2 clusters (main plus lab) is fine.

### 12.6 Results for the plan

- World 11 can use real `kubeadm init`, `join`, upgrade and Calico. Nothing gets dropped.
- The lab cluster used here is now at v1.37.1. Run `cq-cluster lab-down` and `lab-up` before using it for an upgrade level.
- Offline pack needs: the upgrade target images and .debs, Calico images, all level images, per platform.

