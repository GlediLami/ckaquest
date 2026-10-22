"""Writes World 14 (tasks reported from the 2025/2026 exam that no level covered yet)."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
from genlib import level

W = "world-14-exam-reports"
STAGE = '"$CQ_ROOT/cluster/stages.sh"'
BARE_NOTE = """

The bare node is **bare-controlplane** (`ssh bare-controlplane`). It is separate from the game cluster. Your normal kubectl does not talk to it."""
HELM_DOCS = "https://helm.sh/docs/helm/helm_template/"
GW_DOCS = "https://gateway-api.sigs.k8s.io/guides/tls/"
CERT = r"""cert() { openssl req -x509 -newkey rsa:2048 -nodes -days 365 -subj "/CN=$2" -addext "subjectAltName=DNS:$2" -keyout "$1/tls.key" -out "$1/tls.crt" >/dev/null 2>&1; }"""
ECHO = "hashicorp/http-echo:1.0"


def reset(n, *files):
    moves = "; ".join(f'[ -e "$W/{f}" ] && mv -f "$W/{f}" "$W/{f}.old"' for f in files)
    return f'W="$(cq_work_dir {n})"; {moves}; true'


def echo_app(ns, name, text):
    return f"""kubectl create deployment {name} -n {ns} --image={ECHO} -- /http-echo -text="{text}" -listen=:5678 >/dev/null
kubectl expose deployment {name} -n {ns} --port=80 --target-port=5678 >/dev/null"""


# 117 ---------------------------------------------------------------------------------------------
level(W, "level-117-argocd-helm", dict(
    name="Argo CD Without Its CRDs",
    description="The platform team owns the Argo CD CRDs. The chart must not touch them",
    objective="Add a chart repo, render a chart without CRDs to a file, install it",
    xp=300, difficulty="intermediate", expected_time="8m", domain="architecture", course_section=12,
    namespace="argocd", concepts=["helm repo add", "helm template", "chart values", "CRDs managed outside Helm"],
    task="""Argo CD's CRDs are already installed in the cluster. Install Argo CD with Helm, but the chart must not install CRDs.

1. Add the Argo CD chart repository `https://argoproj.github.io/argo-helm` as repo **argo**. Offline, use `http://127.0.0.1:8879` instead. It serves the same chart.
2. Render chart **argo/argo-cd** version **10.10.3** for release **argocd** in namespace **argocd**, with CRD installation turned off. Save the output to `~/ckaquest-work/117/argocd.yaml`.
3. Install the same chart, version and setting as release **argocd** in namespace **argocd**.""",
    docs=[HELM_DOCS, "https://helm.sh/docs/helm/helm_install/", "https://argo-cd.readthedocs.io/en/stable/operator-manual/installation/#helm"]),
    setup=r"""source "$CQ_ROOT/cluster/versions.env"
"$CQ_ROOT/bin/cq-helm-repo" ensure >/dev/null
helm uninstall argocd -n argocd >/dev/null 2>&1
helm repo remove argo >/dev/null 2>&1
""" + reset(117, "argocd.yaml") + r"""
# The CRDs come from the same chart, applied outside Helm like a platform team would
helm template crds "$CQ_HOME/helm-repo/argo-cd-$ARGOCD_CHART_VERSION.tgz" --set crds.install=true \
  | "$CQ_ROOT/venv/bin/python3" -c '
import sys, yaml
docs = [d for d in yaml.safe_load_all(sys.stdin) if d and d.get("kind") == "CustomResourceDefinition"]
print(yaml.safe_dump_all(docs))' | kubectl apply --server-side -f - >/dev/null""",
    validate=r"""F="$CQ_WORK/117/argocd.yaml"
values() { helm get values argocd -n argocd -o json 2>/dev/null; }
check "repo argo is added" out_match "^argo[[:space:]]" helm repo list
check "argocd.yaml exists" file_exists "$F"
check "it renders argocd-server in namespace argocd" bash -c "grep -q 'name: argocd-server' '$F' && grep -q 'namespace: argocd' '$F'"
check 2 "it has no CustomResourceDefinition" bash -c "! grep -q 'kind: CustomResourceDefinition' '$F'"
check 2 "release argocd is deployed with chart argo-cd-10.10.3" out_match "argo-cd-10.10.3.*deployed|deployed.*argo-cd-10.10.3" bash -c "helm list -n argocd | grep '^argocd'"
check "the release has crds.install=false" out_match '"install":false' values
check "Deployment argocd-server exists" exists argocd deploy/argocd-server""",
    solve=r"""source "$CQ_ROOT/cluster/versions.env"
helm repo add argo http://127.0.0.1:8879 >/dev/null
helm repo update argo >/dev/null
helm template argocd argo/argo-cd --version "$ARGOCD_CHART_VERSION" -n argocd --set crds.install=false > "$CQ_WORK/117/argocd.yaml"
helm install argocd argo/argo-cd --version "$ARGOCD_CHART_VERSION" -n argocd --set crds.install=false >/dev/null""",
    cleanup=r"""helm uninstall argocd -n argocd >/dev/null 2>&1
kubectl delete crd applications.argoproj.io applicationsets.argoproj.io appprojects.argoproj.io --ignore-not-found --wait=false >/dev/null 2>&1
helm repo remove argo >/dev/null 2>&1""",
    hints=["`helm show values argo/argo-cd --version 10.10.3 | grep -A3 '^crds'` shows the switch.",
           "`helm template <release> <chart> --version <v> -n <ns> --set <key>=<value> > file`. Without `-n`, the manifests get the wrong namespace.",
           "Install with the same flags. If you forget `crds.install=false`, Helm refuses because the CRDs already exist and are not owned by the release."],
    solution="""```bash
helm repo add argo https://argoproj.github.io/argo-helm     # offline: http://127.0.0.1:8879
helm repo update
helm show values argo/argo-cd --version 10.10.3 | grep -A3 '^crds'
helm template argocd argo/argo-cd --version 10.10.3 -n argocd \\
  --set crds.install=false > ~/ckaquest-work/117/argocd.yaml
helm install argocd argo/argo-cd --version 10.10.3 -n argocd --set crds.install=false
helm list -n argocd
```""",
    debrief="""# Argo CD Without Its CRDs

## What happened
Many charts ship CRDs and have a switch to leave them out, here `crds.install`. Teams turn it off when CRDs are managed separately, for example so an uninstall can never delete every Application.

Helm refuses to take over objects it did not create. With CRDs on, the install fails because the CRDs exist without Helm's ownership labels.

## Patterns
- `helm show values <chart> --version <v>`: find the switch.
- `helm template ... -n <ns> > file`: render, review, or hand to GitOps.
- `helm install` with the same `--version` and `--set`.
- `helm get values <release> -n <ns>`: what a release was installed with.

## Exam angle
- People report this exact task with Argo CD: add repo, template without CRDs to a file, install.
- Always pass `--version` and `-n`. The task usually checks both.

Bookmark: https://helm.sh/docs/helm/helm_template/

Your notes: Helm Basics""")

# 118 ---------------------------------------------------------------------------------------------
level(W, "level-118-tigera-calico", dict(
    name="Calico, the Operator Way",
    description="The new cluster has no pod network. Install Calico with the Tigera operator",
    objective="Install the Tigera operator and an Installation with the cluster's pod CIDR",
    xp=350, difficulty="advanced", expected_time="12m", domain="architecture", course_section=11,
    namespace="lifecycle", context="bare-controlplane",
    concepts=["CNI", "Tigera operator", "Installation custom resource", "cluster-cidr"],
    task="""The cluster on **bare-controlplane** was created with kubeadm but has no CNI. The node is NotReady.

Install Calico with the Tigera operator. The two manifests from the Calico docs are in `/root/`:
1. Create the operator from `/root/tigera-operator.yaml`.
2. Set the IP pool CIDR in `/root/custom-resources.yaml` to the cluster's pod CIDR. Find it in the kube-controller-manager manifest (`--cluster-cidr`). Then create the resources.
3. The node must become Ready.""" + BARE_NOTE,
    docs=["https://docs.tigera.io/calico/latest/getting-started/kubernetes/self-managed-onprem/onpremises",
          "https://kubernetes.io/docs/concepts/cluster-administration/addons/"]),
    setup=STAGE + r""" bare fresh
""" + STAGE + r""" bare init
source "$CQ_ROOT/cluster/versions.env"
for f in tigera-operator.yaml custom-resources.yaml; do
  if [ -s "$CQ_HOME/offline/manifests/$f" ]; then
    docker cp "$CQ_HOME/offline/manifests/$f" "$(cq_node_name bare-controlplane):/root/$f" >/dev/null
  else
    cq_node_sh bare-controlplane "curl -fsSL -o /root/$f https://raw.githubusercontent.com/projectcalico/calico/$CALICO_VERSION/manifests/$f"
  fi
done""",
    validate=r"""K='kubectl --kubeconfig /etc/kubernetes/admin.conf'
check "tigera-operator Deployment is available" node_ok bare-controlplane "$K -n tigera-operator rollout status deploy/tigera-operator --timeout=5s"
check 2 "Installation default uses the pod CIDR 10.50.0.0/16" node_ok bare-controlplane "[ \"\$($K get installation default -o jsonpath='{.spec.calicoNetwork.ipPools[0].cidr}')\" = 10.50.0.0/16 ]"
check 2 "calico-node runs" node_ok bare-controlplane "[ \"\$($K -n calico-system get ds calico-node -o jsonpath='{.status.numberReady}' 2>/dev/null)\" -ge 1 ]"
check 2 "the node is Ready" node_ok bare-controlplane "$K get nodes --no-headers | grep -q ' Ready'" """,
    solve=r"""K='kubectl --kubeconfig /etc/kubernetes/admin.conf'
cq_node_sh bare-controlplane "$K create -f /root/tigera-operator.yaml >/dev/null
cidr=\$(grep -o -- '--cluster-cidr=[^ ]*' /etc/kubernetes/manifests/kube-controller-manager.yaml | cut -d= -f2)
sed -i \"s#cidr: .*#cidr: \$cidr#\" /root/custom-resources.yaml
$K -n tigera-operator rollout status deploy/tigera-operator --timeout=180s >/dev/null
for i in \$(seq 60); do $K create -f /root/custom-resources.yaml >/dev/null 2>&1 && break; $K get installation default >/dev/null 2>&1 && break; sleep 5; done
$K get installation default >/dev/null"
ready() { cq_node_sh bare-controlplane "$K get nodes --no-headers | grep -q ' Ready'"; }
cq_wait 600 ready""",
    cleanup='"$CQ_ROOT/bin/cq-cluster" bare-down >/dev/null 2>&1',
    hints=["`grep cluster-cidr /etc/kubernetes/manifests/kube-controller-manager.yaml`. That is the value for `cidr:`.",
           "Use `kubectl create -f`, not `apply`. The operator's CRDs are too big for the annotation `apply` writes.",
           "After `custom-resources.yaml`, watch `kubectl get tigerastatus` and `kubectl get pods -n calico-system`. It takes a few minutes."],
    solution="""```bash
ssh bare-controlplane
kubectl create -f /root/tigera-operator.yaml
grep cluster-cidr /etc/kubernetes/manifests/kube-controller-manager.yaml   # 10.50.0.0/16
vi /root/custom-resources.yaml        # ipPools[0].cidr: 10.50.0.0/16
kubectl create -f /root/custom-resources.yaml
watch kubectl get tigerastatus,pods -A
kubectl get nodes                     # Ready
```""",
    debrief="""# Calico, the Operator Way

## What happened
The Tigera operator installs and manages Calico. You give it an `Installation` resource that describes what you want. The operator then creates the `calico-system` namespace, calico-node, typha and the kube-controllers.

The IP pool must match the cluster's pod CIDR. kubeadm writes it to kube-controller-manager as `--cluster-cidr`, from `--pod-network-cidr` at init. With a wrong pool, pods get addresses the rest of the cluster does not route.

## Operator or manifest
- Manifest (level 99): one big YAML, you edit `CALICO_IPV4POOL_CIDR` in the DaemonSet.
- Operator: two files, you edit the `Installation`. Upgrades go through the operator.

## Gotchas
- `kubectl create`, not `apply`. The CRDs are bigger than the `last-applied` annotation allows. `kubectl apply --server-side` also works.
- Calico supports NetworkPolicy. Flannel does not. A task that also needs policies wants Calico.

## Exam angle
- Reported with the Tigera docs link in the task. Read the CIDR from the cluster, do not guess.

Bookmark: https://docs.tigera.io/calico/latest/getting-started/kubernetes/self-managed-onprem/onpremises

Your notes: Networking, Cluster Install""")

# 119 ---------------------------------------------------------------------------------------------
level(W, "level-119-pvc-for-given-pv", dict(
    name="The Database Wants Its Old Disk",
    description="A PersistentVolume with the database files is waiting. Claim exactly that one",
    objective="Create a PVC that binds to a given PV and wire it into a Deployment",
    xp=250, difficulty="intermediate", expected_time="8m", domain="storage", course_section=8,
    namespace="mariadb", concepts=["static binding", "storageClassName", "PersistentVolumeClaim", "Deployment volumes"],
    task="""PersistentVolume **mariadb-pv** holds the database files. Look at it first.

1. Create PVC **mariadb** in namespace **mariadb**: access mode ReadWriteOnce, **250Mi**, and the same storage class as the PV. It must bind to **mariadb-pv**.
2. `~/ckaquest-work/119/mariadb-deploy.yaml` is the Deployment. Make it use the PVC and apply it.
3. Deployment **mariadb** must be Ready.

The image is a small stand-in that writes a marker file where MariaDB keeps its data.""",
    docs=["https://kubernetes.io/docs/concepts/storage/persistent-volumes/#binding",
          "https://kubernetes.io/docs/tasks/configure-pod-container/configure-persistent-volume-storage/"]),
    setup=r"""kubectl delete pv mariadb-pv --ignore-not-found --wait=true >/dev/null 2>&1
cat <<EOF | kubectl apply -f - >/dev/null
apiVersion: v1
kind: PersistentVolume
metadata:
  name: mariadb-pv
spec:
  capacity:
    storage: 250Mi
  accessModes: ["ReadWriteOnce"]
  persistentVolumeReclaimPolicy: Retain
  storageClassName: mariadb-storage
  hostPath:
    path: /mnt/mariadb-data
    type: DirectoryOrCreate
  nodeAffinity:
    required:
      nodeSelectorTerms:
      - matchExpressions:
        - key: kubernetes.io/hostname
          operator: In
          values: ["$(cq_node_name node01)"]
EOF
W="$(cq_work_dir 119)"
cat > "$W/mariadb-deploy.yaml" <<'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mariadb
  namespace: mariadb
spec:
  replicas: 1
  selector:
    matchLabels:
      app: mariadb
  template:
    metadata:
      labels:
        app: mariadb
    spec:
      containers:
      - name: mariadb
        image: busybox:1.36
        command: ["sh", "-c", "date > /var/lib/mysql/ready; sleep 3600"]
        volumeMounts:
        - name: data
          mountPath: /var/lib/mysql
      volumes:
      - name: data
        persistentVolumeClaim:
          claimName: ""          # set this
EOF""",
    validate=r"""check 2 "PVC mariadb is Bound to mariadb-pv" out_eq "Bound mariadb-pv" kubectl get pvc mariadb -n mariadb -o jsonpath='{.status.phase} {.spec.volumeName}'
check "PVC requests 250Mi, ReadWriteOnce" out_eq "250Mi ReadWriteOnce" kubectl get pvc mariadb -n mariadb -o jsonpath='{.spec.resources.requests.storage} {.spec.accessModes[0]}'
check "Deployment mariadb uses claim mariadb" field_eq mariadb deploy/mariadb '{.spec.template.spec.volumes[?(@.name=="data")].persistentVolumeClaim.claimName}' mariadb
check 2 "Deployment mariadb is Ready" deploy_ready mariadb mariadb
check "the pod wrote its data to the PV on node01" node_ok node01 'test -s /mnt/mariadb-data/ready'""",
    solve=r"""cat <<'EOF' | kubectl apply -f -
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: mariadb
  namespace: mariadb
spec:
  accessModes: ["ReadWriteOnce"]
  storageClassName: mariadb-storage
  volumeName: mariadb-pv
  resources:
    requests:
      storage: 250Mi
EOF
sed 's/claimName: ""/claimName: mariadb/' "$CQ_WORK/119/mariadb-deploy.yaml" | kubectl apply -f -
kubectl rollout status deploy/mariadb -n mariadb --timeout=120s""",
    cleanup="""kubectl delete pv mariadb-pv --ignore-not-found --wait=false >/dev/null 2>&1""",
    hints=["`k get pv mariadb-pv -o yaml`: note storageClassName, capacity and access mode. The PVC must match them.",
           "Without `storageClassName`, the PVC gets the default class `standard` and a brand new empty volume. `volumeName: mariadb-pv` pins the binding.",
           "Then set `claimName: mariadb` in the file and `k apply -f`."],
    solution="""```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: mariadb
  namespace: mariadb
spec:
  accessModes: ["ReadWriteOnce"]
  storageClassName: mariadb-storage
  volumeName: mariadb-pv
  resources:
    requests:
      storage: 250Mi
```

```bash
k get pv mariadb-pv
k apply -f pvc.yaml
k get pvc -n mariadb                  # Bound
vi ~/ckaquest-work/119/mariadb-deploy.yaml   # claimName: mariadb
k apply -f ~/ckaquest-work/119/mariadb-deploy.yaml
```""",
    debrief="""# The Database Wants Its Old Disk

## What happened
A PVC binds to a PV when class, access mode and size fit. Leave out `storageClassName` and the PVC gets the default class. Then the provisioner creates a new, empty volume and your data stays on the old PV.

`volumeName` names the PV directly. `storageClassName` must still match the PV's class. The class does not have to exist as an object for static binding.

## Retain
`persistentVolumeReclaimPolicy: Retain` keeps the data after the claim is deleted. The PV then shows `Released` and does not bind again until you remove `spec.claimRef`.

## Exam angle
- Reported as "MariaDB with persistent storage": PVC for a given PV, then edit a Deployment file.
- `k get pv` first. Copy class, mode and size exactly.

Bookmark: https://kubernetes.io/docs/concepts/storage/persistent-volumes/#binding

Your notes: Storage""")

# 120 ---------------------------------------------------------------------------------------------
level(W, "level-120-split-node-resources", dict(
    name="Fair Shares",
    description="Three replicas must share node01 evenly",
    objective="Set requests from the node's free allocatable capacity",
    xp=300, difficulty="intermediate", expected_time="10m", domain="workloads", course_section=3,
    namespace="resource-lab", concepts=["node allocatable", "resource requests", "init container requests", "scheduling"],
    task="""Deployment **wordpress** in namespace **resource-lab** runs on **node01** only. It has an init container **init-db** and a container **wordpress**.

1. Scale it to **3** replicas.
2. Set CPU and memory **requests** so the 3 pods share node01 evenly. Look at node01's allocatable capacity and what other pods on it already request. Give each pod about a third of what is free, keeping a little headroom.
3. The init container and the main container get the **same** requests.
4. All 3 pods must be Running on node01.

The containers are stand-ins and use almost nothing. The task is the scheduling math.""",
    docs=["https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/",
          "https://kubernetes.io/docs/tasks/administer-cluster/reserve-compute-resources/#node-allocatable"]),
    setup=r"""cat <<EOF | kubectl apply -f - >/dev/null
apiVersion: apps/v1
kind: Deployment
metadata:
  name: wordpress
  namespace: resource-lab
spec:
  replicas: 1
  selector:
    matchLabels:
      app: wordpress
  template:
    metadata:
      labels:
        app: wordpress
    spec:
      nodeSelector:
        kubernetes.io/hostname: $(cq_node_name node01)
      initContainers:
      - name: init-db
        image: busybox:1.36
        command: ["sh", "-c", "sleep 2"]
      containers:
      - name: wordpress
        image: busybox:1.36
        command: ["sh", "-c", "sleep 3600"]
EOF
kubectl rollout status deploy/wordpress -n resource-lab --timeout=120s >/dev/null 2>&1 || true""",
    validate=r"""N1="$(cq_node_name node01)"
# each wordpress pod must request at least 75% of a third of what other pods leave free on node01
fair() {
  "$CQ_ROOT/venv/bin/python3" - "$N1" <<'EOF'
import json, subprocess, sys
def q(v, cpu):
    if v is None: return 0
    v = str(v)
    if cpu: return float(v[:-1]) / 1000 if v.endswith("m") else float(v)
    for u, f in {"Ki": 2**10, "Mi": 2**20, "Gi": 2**30, "Ti": 2**40, "k": 1e3, "M": 1e6, "G": 1e9}.items():
        if v.endswith(u): return float(v[:-len(u)]) * f
    return float(v)
node = sys.argv[1]
alloc = json.loads(subprocess.check_output(["kubectl", "get", "node", node, "-o", "json"]))["status"]["allocatable"]
pods = json.loads(subprocess.check_output(["kubectl", "get", "pods", "-A", "--field-selector", "spec.nodeName=" + node, "-o", "json"]))["items"]
for res, cpu in (("cpu", True), ("memory", False)):
    used, mine = 0, []
    for p in pods:
        if p["status"].get("phase") in ("Succeeded", "Failed"): continue
        req = sum(q(c.get("resources", {}).get("requests", {}).get(res), cpu) for c in p["spec"]["containers"])
        init = max([q(c.get("resources", {}).get("requests", {}).get(res), cpu) for c in p["spec"].get("initContainers", [])] or [0])
        r = max(req, init)
        if p["metadata"]["namespace"] == "resource-lab": mine.append(r)
        else: used += r
    free = q(alloc[res], cpu) - used
    if len(mine) != 3 or min(mine) < 0.75 * free / 3 or sum(mine) > free:
        sys.exit(1)
EOF
}
same() { local i m; i="$(jp resource-lab deploy/wordpress '{.spec.template.spec.initContainers[0].resources.requests.cpu}/{.spec.template.spec.initContainers[0].resources.requests.memory}')"; m="$(jp resource-lab deploy/wordpress '{.spec.template.spec.containers[0].resources.requests.cpu}/{.spec.template.spec.containers[0].resources.requests.memory}')"; [ -n "${m#/}" ] && [ "$i" = "$m" ]; }
running_n1() { [ "$(kubectl get pods -n resource-lab -l app=wordpress --field-selector=status.phase=Running -o jsonpath='{range .items[*]}{.spec.nodeName}{"\n"}{end}' | grep -cx "$N1")" = 3 ]; }
check "3 replicas" field_eq resource-lab deploy/wordpress '{.spec.replicas}' 3
check "init-db and wordpress request the same CPU and memory" same
check 2 "3 pods Running on node01" running_n1
check 3 "each pod requests about a third of node01's free CPU and memory" fair""",
    solve=r"""N1="$(cq_node_name node01)"
read -r CPU MEM < <("$CQ_ROOT/venv/bin/python3" - "$N1" <<'EOF'
import json, subprocess, sys
def q(v, cpu):
    if v is None: return 0
    v = str(v)
    if cpu: return float(v[:-1]) / 1000 if v.endswith("m") else float(v)
    for u, f in {"Ki": 2**10, "Mi": 2**20, "Gi": 2**30}.items():
        if v.endswith(u): return float(v[:-len(u)]) * f
    return float(v)
node = sys.argv[1]
alloc = json.loads(subprocess.check_output(["kubectl", "get", "node", node, "-o", "json"]))["status"]["allocatable"]
pods = json.loads(subprocess.check_output(["kubectl", "get", "pods", "-A", "--field-selector", "spec.nodeName=" + node, "-o", "json"]))["items"]
out = []
for res, cpu in (("cpu", True), ("memory", False)):
    used = sum(sum(q(c.get("resources", {}).get("requests", {}).get(res), cpu) for c in p["spec"]["containers"])
               for p in pods if p["metadata"]["namespace"] != "resource-lab" and p["status"].get("phase") not in ("Succeeded", "Failed"))
    share = (q(alloc[res], cpu) - used) / 3 * 0.9
    out.append(f"{int(share * 1000)}m" if cpu else f"{int(share / 2**20)}Mi")
print(*out)
EOF
)
kubectl scale deploy/wordpress -n resource-lab --replicas=0 >/dev/null
kubectl patch deploy wordpress -n resource-lab --type=json -p "[
 {\"op\":\"add\",\"path\":\"/spec/template/spec/initContainers/0/resources\",\"value\":{\"requests\":{\"cpu\":\"$CPU\",\"memory\":\"$MEM\"}}},
 {\"op\":\"add\",\"path\":\"/spec/template/spec/containers/0/resources\",\"value\":{\"requests\":{\"cpu\":\"$CPU\",\"memory\":\"$MEM\"}}}]" >/dev/null
kubectl scale deploy/wordpress -n resource-lab --replicas=3 >/dev/null
kubectl rollout status deploy/wordpress -n resource-lab --timeout=120s""",
    hints=["`k describe node node01`: look at **Allocatable** and at **Allocated resources** (what other pods request).",
           "Free = allocatable minus what other pods request. Each pod gets about free / 3. Keep some headroom, about 10%, and lower it if a pod stays Pending.",
           "Scale to 0 first. Otherwise a rolling update needs a 4th pod's worth of room and gets stuck. Set the same requests on `init-db` and `wordpress`, then scale to 3."],
    solution="""```bash
k describe node node01 | grep -A7 -E 'Allocatable|Allocated resources'
# say: allocatable cpu 16, memory 9000Mi. Others request 950m and 290Mi.
# free: 15050m, 8710Mi. Per pod with ~10% headroom: about 4500m, 2600Mi.
k scale deploy wordpress -n resource-lab --replicas=0
k set resources deploy wordpress -n resource-lab -c init-db  --requests=cpu=4500m,memory=2600Mi
k set resources deploy wordpress -n resource-lab -c wordpress --requests=cpu=4500m,memory=2600Mi
k scale deploy wordpress -n resource-lab --replicas=3
k get pods -n resource-lab -o wide
```""",
    debrief="""# Fair Shares

## What happened
The scheduler only looks at **requests**, never at real usage. A pod fits on a node when its requests fit into allocatable capacity minus what the pods already there request.

A pod's request is the larger of two values: the sum of its containers, or its biggest init container. Init containers run before the others, so their requests do not add up.

## The math
1. `k describe node node01`: Allocatable, and "Allocated resources" for the other pods.
2. Free = allocatable minus requests of the others.
3. Per pod = free / replicas, minus some headroom.
4. If a pod stays Pending, `k describe pod` says "Insufficient cpu" or "memory". Lower the request a little.

## The rollout trap
With a RollingUpdate, the new pods start before the old ones go. On a full node they cannot fit. Scale to 0 first, or set the requests before scaling up.

## Exam angle
- Reported: "divide node resources evenly across 3 replicas, with the same requests for init and main". Candidates say fixed rules like "leave 10%" did not always work. Read the node.
- `k set resources` is faster than editing YAML.

Bookmark: https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/

Your notes: Scheduling""")

# 121 ---------------------------------------------------------------------------------------------
level(W, "level-121-tls-configmap", dict(
    name="Old Clients Need TLS 1.2",
    description="The web server only speaks TLS 1.3. Some clients cannot connect",
    objective="Change app config in a ConfigMap, roll it out, and lock the ConfigMap",
    xp=250, difficulty="intermediate", expected_time="8m", domain="workloads", course_section=5,
    namespace="tls-lab", concepts=["ConfigMap", "subPath", "rollout restart", "immutable ConfigMap"],
    task="""Deployment **web** in namespace **tls-lab** runs nginx with HTTPS. Its config comes from ConfigMap **nginx-tls**. It only allows TLS 1.3, and clients that only speak TLS 1.2 fail.

1. Change the ConfigMap so nginx accepts **TLS 1.2 and TLS 1.3**.
2. Make sure the running pods use the new config.
3. Then make ConfigMap **nginx-tls** immutable.

Test with: `curl -k --tls-max 1.2 https://web.tls-lab` from a pod in the cluster.""",
    docs=["https://kubernetes.io/docs/concepts/configuration/configmap/#configmap-immutable",
          "https://kubernetes.io/docs/reference/kubectl/generated/kubectl_rollout/kubectl_rollout_restart/"]),
    setup=CERT + r"""
T="$(mktemp -d "$CQ_HOME/tls-XXXX")"; cert "$T" web.tls-lab
kubectl create secret tls web-tls -n tls-lab --cert="$T/tls.crt" --key="$T/tls.key" >/dev/null
mv "$T" "$CQ_HOME/backup/tls-121-$(date +%s)"
cat <<'EOF' | kubectl apply -f - >/dev/null
apiVersion: v1
kind: ConfigMap
metadata:
  name: nginx-tls
  namespace: tls-lab
data:
  default.conf: |
    server {
      listen 443 ssl;
      server_name web.tls-lab;
      ssl_certificate     /etc/nginx/tls/tls.crt;
      ssl_certificate_key /etc/nginx/tls/tls.key;
      ssl_protocols TLSv1.3;
      location / { return 200 "tls ok\n"; }
    }
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
  namespace: tls-lab
spec:
  replicas: 1
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
      - name: nginx
        image: nginx:1.27
        ports:
        - containerPort: 443
        volumeMounts:
        - name: conf
          mountPath: /etc/nginx/conf.d/default.conf
          subPath: default.conf
        - name: tls
          mountPath: /etc/nginx/tls
          readOnly: true
      volumes:
      - name: conf
        configMap:
          name: nginx-tls
      - name: tls
        secret:
          secretName: web-tls
---
apiVersion: v1
kind: Service
metadata:
  name: web
  namespace: tls-lab
spec:
  selector:
    app: web
  ports:
  - port: 443
    targetPort: 443
EOF
kubectl rollout status deploy/web -n tls-lab --timeout=120s >/dev/null 2>&1 || true""",
    validate=r"""tls12() { in_cluster_out tls-lab curlimages/curl:8.11.1 curl -sk -m 5 --tlsv1.2 --tls-max 1.2 https://web.tls-lab/ | grep -q "tls ok"; }
tls13() { in_cluster_out tls-lab curlimages/curl:8.11.1 curl -sk -m 5 --tlsv1.3 https://web.tls-lab/ | grep -q "tls ok"; }
check "the ConfigMap allows TLSv1.2 and TLSv1.3" out_match "ssl_protocols +(TLSv1\.2 +TLSv1\.3|TLSv1\.3 +TLSv1\.2) *;" kubectl get cm nginx-tls -n tls-lab -o jsonpath='{.data.default\.conf}'
check 3 "a TLS 1.2 client gets 'tls ok'" tls12
check "a TLS 1.3 client still works" tls13
check 2 "ConfigMap nginx-tls is immutable" field_eq tls-lab cm/nginx-tls '{.immutable}' true""",
    solve=r"""kubectl get cm nginx-tls -n tls-lab -o yaml | sed 's/ssl_protocols TLSv1.3;/ssl_protocols TLSv1.2 TLSv1.3;/' | kubectl apply -f - >/dev/null
kubectl patch cm nginx-tls -n tls-lab -p '{"immutable":true}' >/dev/null
kubectl rollout restart deploy/web -n tls-lab >/dev/null
kubectl rollout status deploy/web -n tls-lab --timeout=120s""",
    hints=["`k edit cm nginx-tls -n tls-lab`: the line is `ssl_protocols`.",
           "The ConfigMap is mounted with `subPath`. Those files never update in a running pod. `k rollout restart deploy/web -n tls-lab`.",
           "`k patch cm nginx-tls -n tls-lab -p '{\"immutable\":true}'`. Do this last. Afterwards the data cannot change any more."],
    solution="""```bash
k edit cm nginx-tls -n tls-lab        # ssl_protocols TLSv1.2 TLSv1.3;
k rollout restart deploy/web -n tls-lab
k rollout status deploy/web -n tls-lab
k run t -n tls-lab --rm -it --image=curlimages/curl:8.11.1 --restart=Never -- \\
  curl -k --tls-max 1.2 https://web.tls-lab
k patch cm nginx-tls -n tls-lab -p '{"immutable":true}'
```""",
    debrief="""# Old Clients Need TLS 1.2

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

Your notes: ConfigMaps and Secrets""")

# 122 ---------------------------------------------------------------------------------------------
level(W, "level-122-cert-manager-crds", dict(
    name="Read the Operator's Manual",
    description="cert-manager is installed. Find its types and read one field's documentation",
    objective="List an operator's CRDs and use kubectl explain on a custom resource",
    xp=200, difficulty="beginner", expected_time="5m", domain="architecture", course_section=7,
    namespace="cert-lab", concepts=["CustomResourceDefinition", "kubectl explain", "operators"],
    task="""cert-manager's CRDs are installed in the cluster.

1. Write all cert-manager CRDs to `~/ckaquest-work/122/crds.txt`. Use kubectl's normal output, one CRD per line.
2. Write the documentation of field **spec.subject** of the **Certificate** resource to `~/ckaquest-work/122/subject.txt`. Use kubectl, not the website.""",
    docs=["https://kubernetes.io/docs/reference/kubectl/generated/kubectl_explain/",
          "https://cert-manager.io/docs/reference/api-docs/"]),
    setup=reset(122, "crds.txt", "subject.txt") + r"""
source "$CQ_ROOT/cluster/versions.env"
src="$CQ_HOME/offline/manifests/cert-manager.crds.yaml"
if [ -s "$src" ]; then kubectl apply --server-side -f "$src" >/dev/null
else kubectl apply --server-side -f "https://github.com/cert-manager/cert-manager/releases/download/$CERT_MANAGER_VERSION/cert-manager.crds.yaml" >/dev/null; fi
kubectl wait --for=condition=Established crd/certificates.cert-manager.io --timeout=60s >/dev/null""",
    validate=r"""F="$CQ_WORK/122/crds.txt"; S="$CQ_WORK/122/subject.txt"
all_listed() { local c; for c in $(kubectl get crd -o name | grep cert-manager.io | cut -d/ -f2); do grep -q "$c" "$F" || return 1; done; }
only_cm() { ! grep -v -e cert-manager -e '^NAME' "$F" | grep -q .; }
check "crds.txt exists" file_exists "$F"
check 2 "it lists every cert-manager CRD" all_listed
check "it lists nothing else" only_cm
check "subject.txt exists" file_exists "$S"
check 2 "subject.txt is the explain output for Certificate spec.subject" bash -c "grep -q 'KIND: *Certificate' '$S' && grep -qi 'FIELD: *subject' '$S' && grep -q 'organizations' '$S'" """,
    solve=r"""kubectl get crd | grep cert-manager > "$CQ_WORK/122/crds.txt"
kubectl explain certificate.spec.subject > "$CQ_WORK/122/subject.txt" """,
    cleanup="""kubectl get crd -o name | grep cert-manager.io | xargs -r kubectl delete --wait=false >/dev/null 2>&1""",
    hints=["`k get crd | grep cert-manager`. Redirect it with `>`.",
           "`k explain` works for custom resources too, once their CRD has a schema.",
           "`k explain certificate.spec.subject > ~/ckaquest-work/122/subject.txt`. Add `--api-version=cert-manager.io/v1` if two groups had a Certificate kind."],
    solution="""```bash
k get crd | grep cert-manager > ~/ckaquest-work/122/crds.txt
k explain certificate.spec.subject > ~/ckaquest-work/122/subject.txt
cat ~/ckaquest-work/122/subject.txt
```""",
    debrief="""# Read the Operator's Manual

## What happened
An operator is a controller plus CRDs. The CRDs carry an OpenAPI schema, so `kubectl explain` documents custom resources exactly like built-in ones.

## Useful commands
- `k get crd | grep <name>`: the types an operator adds.
- `k api-resources --api-group=cert-manager.io`: short names and scope.
- `k explain <kind>.<field> --recursive`: the whole tree of a field.

## Exam angle
- Reported as "list the cert-manager CRDs to a file, save the explain output of Certificate spec.subject".
- Save exactly what kubectl prints. No editing, no extra lines.

Bookmark: https://kubernetes.io/docs/reference/kubectl/generated/kubectl_explain/

Your notes: CRDs and Operators""")

# 123 ---------------------------------------------------------------------------------------------
level(W, "level-123-ingress-to-https-gateway", dict(
    name="Retire the Ingress",
    description="Move an HTTPS Ingress to a new Gateway of its own",
    objective="Create an HTTPS Gateway and an HTTPRoute that replace an Ingress",
    xp=350, difficulty="advanced", expected_time="12m", domain="networking", course_section=9,
    namespace="shop-migrate", requires=["gateway"],
    concepts=["Gateway", "HTTPS listener", "TLS terminate", "HTTPRoute", "Ingress migration"],
    task="""Ingress **shop** in namespace **shop-migrate** serves `https://shop.example.com` with the TLS Secret **shop-tls**:
- path prefix `/api` to Service **api** port 80
- path prefix `/` to Service **web** port 80

Replace it with Gateway API:
1. Create Gateway **shop-gw** in **shop-migrate** with the existing GatewayClass **nginx**. Listener **https**: port 443, protocol HTTPS, hostname `shop.example.com`, TLS terminate with Secret **shop-tls**.
2. Create HTTPRoute **shop-route** attached to it, with the same rules as the Ingress.
3. Delete Ingress **shop**.""",
    docs=[GW_DOCS, "https://gateway-api.sigs.k8s.io/guides/migrating-from-ingress/",
          "https://kubernetes.io/docs/concepts/services-networking/gateway/"]),
    setup=CERT + r"""
T="$(mktemp -d "$CQ_HOME/tls-XXXX")"; cert "$T" shop.example.com
kubectl create secret tls shop-tls -n shop-migrate --cert="$T/tls.crt" --key="$T/tls.key" >/dev/null
mv "$T" "$CQ_HOME/backup/tls-123-$(date +%s)"
""" + echo_app("shop-migrate", "api", "shop api") + "\n" + echo_app("shop-migrate", "web", "shop web") + r"""
cat <<'EOF' | kubectl apply -f - >/dev/null
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: shop
  namespace: shop-migrate
spec:
  ingressClassName: nginx
  tls:
  - hosts: ["shop.example.com"]
    secretName: shop-tls
  rules:
  - host: shop.example.com
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: api
            port:
              number: 80
      - path: /
        pathType: Prefix
        backend:
          service:
            name: web
            port:
              number: 80
EOF""",
    validate=r"""gwip() { kubectl get svc -n shop-migrate -l gateway.networking.k8s.io/gateway-name=shop-gw -o jsonpath='{.items[0].spec.clusterIP}'; }
get() { in_cluster_out shop-migrate curlimages/curl:8.11.1 curl -sk -m 5 --resolve "shop.example.com:443:$(gwip)" "https://shop.example.com$1"; }
listener() { kubectl get gateway shop-gw -n shop-migrate -o jsonpath='{range .spec.listeners[?(@.name=="https")]}{.protocol} {.port} {.hostname} {.tls.mode} {.tls.certificateRefs[0].name}{end}'; }
check "Gateway shop-gw uses class nginx" field_eq shop-migrate gateway/shop-gw '{.spec.gatewayClassName}' nginx
check 2 "listener https: HTTPS 443 shop.example.com Terminate shop-tls" out_eq "HTTPS 443 shop.example.com Terminate shop-tls" listener
check "HTTPRoute shop-route is attached to shop-gw" field_eq shop-migrate httproute/shop-route '{.spec.parentRefs[0].name}' shop-gw
check 2 "https://shop.example.com/api answers 'shop api'" out_match "shop api" get /api
check 2 "https://shop.example.com/ answers 'shop web'" out_match "shop web" get /
check "Ingress shop is deleted" not_exists shop-migrate ingress/shop""",
    solve=r"""cat <<'EOF' | kubectl apply -f -
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: shop-gw
  namespace: shop-migrate
spec:
  gatewayClassName: nginx
  listeners:
  - name: https
    protocol: HTTPS
    port: 443
    hostname: shop.example.com
    tls:
      mode: Terminate
      certificateRefs:
      - name: shop-tls
---
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: shop-route
  namespace: shop-migrate
spec:
  parentRefs:
  - name: shop-gw
  hostnames: ["shop.example.com"]
  rules:
  - matches:
    - path:
        type: PathPrefix
        value: /api
    backendRefs:
    - name: api
      port: 80
  - matches:
    - path:
        type: PathPrefix
        value: /
    backendRefs:
    - name: web
      port: 80
EOF
kubectl delete ingress shop -n shop-migrate
up() { [ -n "$(kubectl get svc -n shop-migrate -l gateway.networking.k8s.io/gateway-name=shop-gw -o jsonpath='{.items[0].spec.clusterIP}')" ] && kubectl get gateway shop-gw -n shop-migrate -o jsonpath='{.status.conditions[?(@.type=="Programmed")].status}' | grep -q True; }
cq_wait 180 up; sleep 20""",
    hints=["`k get ingress shop -n shop-migrate -o yaml`: copy host, TLS secret and the two paths.",
           "Gateway: `gatewayClassName: nginx`, a listener with `protocol: HTTPS`, `port: 443`, `hostname`, and `tls.mode: Terminate` with `certificateRefs: [{name: shop-tls}]`.",
           "HTTPRoute: `parentRefs: [{name: shop-gw}]`, `hostnames`, one rule per path with `PathPrefix`. The new Gateway gets its own data plane. Give it a minute before testing."],
    solution="""```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: shop-gw
  namespace: shop-migrate
spec:
  gatewayClassName: nginx
  listeners:
  - name: https
    protocol: HTTPS
    port: 443
    hostname: shop.example.com
    tls:
      mode: Terminate
      certificateRefs:
      - name: shop-tls
---
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: shop-route
  namespace: shop-migrate
spec:
  parentRefs:
  - name: shop-gw
  hostnames: ["shop.example.com"]
  rules:
  - matches: [{path: {type: PathPrefix, value: /api}}]
    backendRefs: [{name: api, port: 80}]
  - matches: [{path: {type: PathPrefix, value: /}}]
    backendRefs: [{name: web, port: 80}]
```

```bash
k apply -f gw.yaml
k get gateway,httproute -n shop-migrate
k delete ingress shop -n shop-migrate
```""",
    debrief="""# Retire the Ingress

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

Your notes: Gateway API""")

# 124 ---------------------------------------------------------------------------------------------
level(W, "level-124-priorityclass-patch", dict(
    name="Just Below the Top",
    description="The logger must win against almost everything, but not against the top class",
    objective="Create a PriorityClass from existing values and patch a Deployment",
    xp=200, difficulty="intermediate", expected_time="5m", domain="workloads", course_section=3,
    namespace="priority-lab", concepts=["PriorityClass", "kubectl patch", "pod priority"],
    task="""1. Create PriorityClass **high-priority**. Its value is **one less** than the highest value of the existing **user-defined** PriorityClasses (ignore the built-in `system-` classes).
2. Make Deployment **busybox-logger** in namespace **priority-lab** use it. Use `kubectl patch`, not edit.""",
    docs=["https://kubernetes.io/docs/concepts/scheduling-eviction/pod-priority-preemption/",
          "https://kubernetes.io/docs/tasks/manage-kubernetes-objects/update-api-object-kubectl-patch/"]),
    setup=r"""kubectl delete priorityclass high-priority --ignore-not-found >/dev/null 2>&1
for pc in "batch-low 1000" "team-standard 250000" "team-critical 750000"; do
  set -- $pc
  kubectl create priorityclass "$1" --value="$2" >/dev/null 2>&1 || true
done
kubectl create deployment busybox-logger -n priority-lab --image=busybox:1.36 -- sh -c "while true; do echo log; sleep 10; done" >/dev/null
kubectl rollout status deploy/busybox-logger -n priority-lab --timeout=120s >/dev/null 2>&1 || true""",
    validate=r"""want() { echo $(( $(kubectl get priorityclass -o jsonpath='{range .items[*]}{.metadata.name} {.value}{"\n"}{end}' | grep -v -e '^system-' -e '^high-priority ' | awk '{print $2}' | sort -n | tail -1) - 1 )); }
pod_prio() { kubectl get pods -n priority-lab -l app=busybox-logger --field-selector=status.phase=Running -o jsonpath='{.items[*].spec.priority}'; }
check 2 "high-priority is one less than the highest user-defined class" out_eq "$(want)" kubectl get priorityclass high-priority -o jsonpath='{.value}'
check 2 "busybox-logger uses high-priority" field_eq priority-lab deploy/busybox-logger '{.spec.template.spec.priorityClassName}' high-priority
check "its pod runs with that priority" out_eq "$(want)" pod_prio""",
    solve=r"""top=$(kubectl get priorityclass -o jsonpath='{range .items[*]}{.metadata.name} {.value}{"\n"}{end}' | grep -v '^system-' | awk '{print $2}' | sort -n | tail -1)
kubectl create priorityclass high-priority --value=$((top - 1))
kubectl patch deploy busybox-logger -n priority-lab -p '{"spec":{"template":{"spec":{"priorityClassName":"high-priority"}}}}'
kubectl rollout status deploy/busybox-logger -n priority-lab --timeout=120s
gone() { [ "$(kubectl get pods -n priority-lab -l app=busybox-logger --no-headers | wc -l)" = 1 ]; }
cq_wait 60 gone""",
    cleanup="""kubectl delete priorityclass high-priority batch-low team-standard team-critical --ignore-not-found >/dev/null 2>&1""",
    hints=["`k get priorityclass` and sort by VALUE. Skip `system-cluster-critical` and `system-node-critical`.",
           "`k create priorityclass high-priority --value=<n>`.",
           "`k patch deploy busybox-logger -n priority-lab -p '{\"spec\":{\"template\":{\"spec\":{\"priorityClassName\":\"high-priority\"}}}}'`"],
    solution="""```bash
k get priorityclass --sort-by=.value
k create priorityclass high-priority --value=749999
k patch deploy busybox-logger -n priority-lab \\
  -p '{"spec":{"template":{"spec":{"priorityClassName":"high-priority"}}}}'
k get pod -n priority-lab -o jsonpath='{.items[*].spec.priority}'
```""",
    debrief="""# Just Below the Top

## What happened
A PriorityClass maps a name to a number. Pods with a higher priority are scheduled first and can preempt lower ones when the cluster is full. The built-in `system-cluster-critical` and `system-node-critical` sit far above every user class (2,000,000,000 and more). Never compete with them.

Admission writes the value into `pod.spec.priority` when the pod is created. Changing the Deployment rolls new pods with the new priority.

## kubectl patch
- strategic merge (default): `-p '{"spec":{...}}'`, merges like `apply`.
- `--type=merge`: plain JSON merge.
- `--type=json`: a list of operations, for list items and removals.

## Exam angle
- Reported: "a PriorityClass one less than the highest user-defined one, add it to a Deployment with kubectl patch only".
- `k get pc --sort-by=.value` gives the number fast.

Bookmark: https://kubernetes.io/docs/concepts/scheduling-eviction/pod-priority-preemption/

Your notes: Scheduling""")

# 125 ---------------------------------------------------------------------------------------------
level(W, "level-125-sidecar-deployment", dict(
    name="A Reader Next to the Writer",
    description="The app writes logs to a file nobody can see",
    objective="Add a log-reading sidecar to an existing Deployment with a shared volume",
    xp=250, difficulty="intermediate", expected_time="8m", domain="workloads", course_section=5,
    namespace="logs-lab", concepts=["co-located containers", "emptyDir", "volumeMounts", "kubectl logs -c"],
    task="""Deployment **app-logger** in namespace **logs-lab** has a container **app** that writes to `/var/log/app.log` inside the container. `kubectl logs` shows nothing.

Update the Deployment:
1. Add a volume **logs** (emptyDir) and mount it at `/var/log` in container **app**.
2. Add a container **sidecar**, image `busybox:1.36`, command `/bin/sh -c "tail -n+1 -f /var/log/app.log"`, with the same volume at `/var/log`.
3. `kubectl logs` of container **sidecar** must show the app's lines.""",
    docs=["https://kubernetes.io/docs/concepts/cluster-administration/logging/#sidecar-container-with-logging-agent",
          "https://kubernetes.io/docs/tasks/access-application-cluster/communicate-containers-same-pod-shared-volume/"]),
    setup=r"""cat <<'EOF' | kubectl apply -f - >/dev/null
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-logger
  namespace: logs-lab
spec:
  replicas: 1
  selector:
    matchLabels:
      app: app-logger
  template:
    metadata:
      labels:
        app: app-logger
    spec:
      containers:
      - name: app
        image: busybox:1.36
        command: ["sh", "-c", "i=0; while true; do i=$((i+1)); echo \"$(date) request $i done\" >> /var/log/app.log; sleep 2; done"]
EOF
kubectl rollout status deploy/app-logger -n logs-lab --timeout=120s >/dev/null 2>&1 || true""",
    validate=r"""C='{.spec.template.spec.containers'
mount() { kubectl get deploy app-logger -n logs-lab -o jsonpath="$C[?(@.name==\"$1\")].volumeMounts[?(@.name==\"logs\")].mountPath}"; }
sidecar_cmd() { kubectl get deploy app-logger -n logs-lab -o jsonpath="$C[?(@.name==\"sidecar\")].command}$C[?(@.name==\"sidecar\")].args}"; }
reads() { kubectl logs deploy/app-logger -n logs-lab -c sidecar --tail=5 2>/dev/null | grep -q "request"; }
check "volume logs is an emptyDir" out_eq '{}' kubectl get deploy app-logger -n logs-lab -o jsonpath='{.spec.template.spec.volumes[?(@.name=="logs")].emptyDir}'
check "app mounts logs at /var/log" out_eq /var/log mount app
check "sidecar mounts logs at /var/log" out_eq /var/log mount sidecar
check "sidecar runs tail -f on /var/log/app.log" out_match 'tail.*-[fF].*/var/log/app.log|tail.*/var/log/app.log.*-[fF]' sidecar_cmd
check "Deployment is Ready" deploy_ready logs-lab app-logger
check 3 "kubectl logs -c sidecar shows the app's lines" reads""",
    solve=r"""kubectl patch deploy app-logger -n logs-lab --type=strategic -p '{"spec":{"template":{"spec":{
 "volumes":[{"name":"logs","emptyDir":{}}],
 "containers":[
  {"name":"app","volumeMounts":[{"name":"logs","mountPath":"/var/log"}]},
  {"name":"sidecar","image":"busybox:1.36","command":["/bin/sh","-c","tail -n+1 -f /var/log/app.log"],"volumeMounts":[{"name":"logs","mountPath":"/var/log"}]}]}}}}'
kubectl rollout status deploy/app-logger -n logs-lab --timeout=120s
sleep 8""",
    hints=["`k edit deploy app-logger -n logs-lab`. Add `volumes:` at the pod level, next to `containers:`.",
           "Both containers get `volumeMounts: [{name: logs, mountPath: /var/log}]`.",
           "Errors from the sidecar in the first seconds (file not found yet) are fine. It catches up. Check with `k logs deploy/app-logger -n logs-lab -c sidecar`."],
    solution="""```yaml
spec:
  template:
    spec:
      volumes:
      - name: logs
        emptyDir: {}
      containers:
      - name: app
        # ...unchanged...
        volumeMounts:
        - name: logs
          mountPath: /var/log
      - name: sidecar
        image: busybox:1.36
        command: ["/bin/sh", "-c", "tail -n+1 -f /var/log/app.log"]
        volumeMounts:
        - name: logs
          mountPath: /var/log
```

```bash
k edit deploy app-logger -n logs-lab
k logs deploy/app-logger -n logs-lab -c sidecar
```""",
    debrief="""# A Reader Next to the Writer

## What happened
`kubectl logs` only shows what a container writes to stdout and stderr. An app that logs to a file is invisible. A second container in the same pod can read that file through a shared volume and print it to its own stdout.

## Two ways
- Plain second container (this level, and what the reported task asked): starts together with the app, no order.
- Native sidecar (level 87): an init container with `restartPolicy: Always`. Starts first and does not block Jobs from finishing.

Read the task. "Add a container named sidecar" means a normal container. "A sidecar that starts first" means the native one.

## Exam angle
- Reported: "update a Deployment with a co-located container that runs tail -f on the shared log". Candidates say early `tail` errors in the logs are a trick, ignore them if the pod runs.

Bookmark: https://kubernetes.io/docs/concepts/cluster-administration/logging/

Your notes: Multi-Container Pods""")

# 126 ---------------------------------------------------------------------------------------------
level(W, "level-126-wffc-by-hand", dict(
    name="Bound Only When Needed",
    description="Build local storage from scratch and watch the claim wait for its pod",
    objective="Create a StorageClass with WaitForFirstConsumer, a local PV, a PVC and a pod",
    xp=300, difficulty="intermediate", expected_time="10m", domain="storage", course_section=8,
    namespace="wffc-lab", concepts=["StorageClass", "WaitForFirstConsumer", "local PersistentVolume", "node affinity"],
    task="""Build local storage on **node02** by hand. The directory `/mnt/wffc` exists on node02.

1. StorageClass **local-wffc**: provisioner `kubernetes.io/no-provisioner`, volume binding mode **WaitForFirstConsumer**.
2. PersistentVolume **wffc-pv**: 200Mi, ReadWriteOnce, class local-wffc, a **local** volume at `/mnt/wffc`, only on node02.
3. PVC **wffc-pvc** in namespace **wffc-lab**: 200Mi, ReadWriteOnce, class local-wffc. Check its status. It stays Pending, and that is correct.
4. Pod **wffc-pod** (`busybox:1.36`, `sleep 3600`) that mounts the PVC at `/data`. Now the PVC must become Bound.""",
    docs=["https://kubernetes.io/docs/concepts/storage/storage-classes/#local",
          "https://kubernetes.io/docs/concepts/storage/volumes/#local"]),
    setup=r"""kubectl delete pv wffc-pv --ignore-not-found >/dev/null 2>&1
kubectl delete sc local-wffc --ignore-not-found >/dev/null 2>&1
cq_node_sh node02 'mkdir -p /mnt/wffc'""",
    validate=r"""N2="$(cq_node_name node02)"
check "StorageClass local-wffc: no-provisioner, WaitForFirstConsumer" out_eq "kubernetes.io/no-provisioner WaitForFirstConsumer" kubectl get sc local-wffc -o jsonpath='{.provisioner} {.volumeBindingMode}'
check "PV wffc-pv: 200Mi, ReadWriteOnce, local-wffc, local /mnt/wffc" out_eq "200Mi ReadWriteOnce local-wffc /mnt/wffc" kubectl get pv wffc-pv -o jsonpath='{.spec.capacity.storage} {.spec.accessModes[0]} {.spec.storageClassName} {.spec.local.path}'
check "PV wffc-pv only on node02" field_eq - pv/wffc-pv '{.spec.nodeAffinity.required.nodeSelectorTerms[0].matchExpressions[0].values[0]}' "$N2"
check 2 "PVC wffc-pvc is Bound to wffc-pv" out_eq "Bound wffc-pv" kubectl get pvc wffc-pvc -n wffc-lab -o jsonpath='{.status.phase} {.spec.volumeName}'
check 2 "wffc-pod runs on node02 with /data mounted" out_eq "Running $N2 wffc-pvc" kubectl get pod wffc-pod -n wffc-lab -o jsonpath='{.status.phase} {.spec.nodeName} {.spec.volumes[0].persistentVolumeClaim.claimName}'""",
    solve=r"""cat <<EOF | kubectl apply -f -
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: local-wffc
provisioner: kubernetes.io/no-provisioner
volumeBindingMode: WaitForFirstConsumer
---
apiVersion: v1
kind: PersistentVolume
metadata:
  name: wffc-pv
spec:
  capacity:
    storage: 200Mi
  accessModes: ["ReadWriteOnce"]
  storageClassName: local-wffc
  local:
    path: /mnt/wffc
  nodeAffinity:
    required:
      nodeSelectorTerms:
      - matchExpressions:
        - key: kubernetes.io/hostname
          operator: In
          values: ["$(cq_node_name node02)"]
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: wffc-pvc
  namespace: wffc-lab
spec:
  accessModes: ["ReadWriteOnce"]
  storageClassName: local-wffc
  resources:
    requests:
      storage: 200Mi
---
apiVersion: v1
kind: Pod
metadata:
  name: wffc-pod
  namespace: wffc-lab
spec:
  containers:
  - name: app
    image: busybox:1.36
    command: ["sleep", "3600"]
    volumeMounts:
    - name: data
      mountPath: /data
  volumes:
  - name: data
    persistentVolumeClaim:
      claimName: wffc-pvc
EOF
kubectl wait --for=condition=Ready pod/wffc-pod -n wffc-lab --timeout=120s""",
    cleanup="""kubectl delete pod wffc-pod -n wffc-lab --ignore-not-found --wait=false >/dev/null 2>&1
kubectl delete pvc wffc-pvc -n wffc-lab --ignore-not-found --wait=false >/dev/null 2>&1
kubectl delete pv wffc-pv --ignore-not-found --wait=false >/dev/null 2>&1
kubectl delete sc local-wffc --ignore-not-found >/dev/null 2>&1""",
    hints=["The docs page for StorageClass, section **Local**, has the StorageClass. Volumes, section **local**, has the PV with `nodeAffinity`.",
           "A `local` PV must have `nodeAffinity`. Use `kubernetes.io/hostname` with node02's real name (`k get nodes`).",
           "`k get pvc -n wffc-lab` shows Pending with the event `WaitForFirstConsumer`. That is right. Create the pod and check again."],
    solution="""```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: local-wffc
provisioner: kubernetes.io/no-provisioner
volumeBindingMode: WaitForFirstConsumer
---
apiVersion: v1
kind: PersistentVolume
metadata:
  name: wffc-pv
spec:
  capacity: {storage: 200Mi}
  accessModes: ["ReadWriteOnce"]
  storageClassName: local-wffc
  local:
    path: /mnt/wffc
  nodeAffinity:
    required:
      nodeSelectorTerms:
      - matchExpressions:
        - {key: kubernetes.io/hostname, operator: In, values: [<node02 name>]}
```

```bash
k apply -f storage.yaml
k apply -f pvc.yaml; k get pvc -n wffc-lab        # Pending
k apply -f pod.yaml;  k get pvc -n wffc-lab        # Bound
```""",
    debrief="""# Bound Only When Needed

## What happened
With `Immediate` binding, a PVC binds as soon as a fitting PV exists. For node-local storage that can be wrong: the PV is on node02, but the pod might need to run elsewhere.

`WaitForFirstConsumer` delays binding until a pod using the PVC is scheduled. The scheduler then picks a node that fits both the pod and the PV's `nodeAffinity`. Until then the PVC is Pending with the event "waiting for first consumer to be created before binding".

## Local volumes
- `provisioner: kubernetes.io/no-provisioner`: nothing creates PVs, you do.
- `local.path` must exist on the node.
- `nodeAffinity` is required. It tells the scheduler where the disk is.

## Exam angle
- Reported: "create SC with WaitForFirstConsumer, PV and PVC, observe Pending, create a pod, verify Bound".
- Pending here is not a bug. Read the PVC events before you change anything.

Bookmark: https://kubernetes.io/docs/concepts/storage/storage-classes/#local

Your notes: Storage""")

# 127 ---------------------------------------------------------------------------------------------
level(W, "level-127-ingress-tls", dict(
    name="Lock the Front Door",
    description="The app is only reachable over plain HTTP",
    objective="Create a TLS Secret and an Ingress that terminates HTTPS",
    xp=250, difficulty="intermediate", expected_time="7m", domain="networking", course_section=9,
    namespace="tls-ingress", requires=["ingress"],
    concepts=["Ingress TLS", "kubernetes.io/tls Secret", "ingressClassName"],
    task="""Service **app** in namespace **tls-ingress** listens on port 80. A certificate and key for `secure.example.com` are in `~/ckaquest-work/127/` (`tls.crt`, `tls.key`).

1. Create TLS Secret **app-tls** in **tls-ingress** from them.
2. Create Ingress **app-ingress** with IngressClass **nginx** for host `secure.example.com`: path prefix `/` to Service **app** port 80, and TLS with Secret **app-tls**.

`https://secure.example.com` must reach the app.""",
    docs=["https://kubernetes.io/docs/concepts/services-networking/ingress/#tls",
          "https://kubernetes.io/docs/concepts/configuration/secret/#tls-secrets"]),
    setup=CERT + r"""
W="$(cq_work_dir 127)"
cert "$W" secure.example.com
""" + echo_app("tls-ingress", "app", "secure app"),
    validate=r"""ctrl() { kubectl get svc ingress-nginx-controller -n ingress-nginx -o jsonpath='{.spec.clusterIP}'; }
https_ok() { kubectl run "cq-wait-$RANDOM" -n tls-ingress --image=curlimages/curl:8.11.1 --restart=Never --rm -i --quiet --command -- curl -sk -m 5 --resolve "secure.example.com:443:$(ctrl)" https://secure.example.com/ | grep -q "secure app"; }
check "Secret app-tls is type kubernetes.io/tls" field_eq tls-ingress secret/app-tls '{.type}' kubernetes.io/tls
check "Ingress uses class nginx" field_eq tls-ingress ing/app-ingress '{.spec.ingressClassName}' nginx
check 2 "TLS for secure.example.com with app-tls" out_eq "secure.example.com app-tls" kubectl get ing app-ingress -n tls-ingress -o jsonpath='{.spec.tls[0].hosts[0]} {.spec.tls[0].secretName}'
check 3 "https://secure.example.com answers 'secure app'" https_ok""",
    solve=r"""kubectl create secret tls app-tls -n tls-ingress --cert="$CQ_WORK/127/tls.crt" --key="$CQ_WORK/127/tls.key"
kubectl create ingress app-ingress -n tls-ingress --class=nginx --rule="secure.example.com/*=app:80,tls=app-tls"
ok() { kubectl run "cq-wait-$RANDOM" -n tls-ingress --image=curlimages/curl:8.11.1 --restart=Never --rm -i --quiet --command -- curl -sk -m 5 --resolve "secure.example.com:443:$(kubectl get svc ingress-nginx-controller -n ingress-nginx -o jsonpath='{.spec.clusterIP}')" https://secure.example.com/ | grep -q "secure app"; }
cq_wait 240 ok""",
    hints=["`k create secret tls app-tls -n tls-ingress --cert=... --key=...`",
           "`k create ingress --help` shows the `tls=` part of `--rule`.",
           "`k create ingress app-ingress -n tls-ingress --class=nginx --rule=\"secure.example.com/*=app:80,tls=app-tls\"`"],
    solution="""```bash
k create secret tls app-tls -n tls-ingress \\
  --cert=~/ckaquest-work/127/tls.crt --key=~/ckaquest-work/127/tls.key
k create ingress app-ingress -n tls-ingress --class=nginx \\
  --rule="secure.example.com/*=app:80,tls=app-tls"
k get ingress app-ingress -n tls-ingress -o yaml
```""",
    debrief="""# Lock the Front Door

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

Your notes: Ingress""")

# 128 ---------------------------------------------------------------------------------------------
level(W, "level-128-local-chart", dict(
    name="A Chart on Disk",
    description="The chart is a folder, not a repo, and the namespace does not exist yet",
    objective="Install a chart from a local directory with overrides into a new namespace",
    xp=200, difficulty="beginner", expected_time="5m", domain="architecture", course_section=12,
    namespace="helm-local", concepts=["helm install from a directory", "--set", "--create-namespace"],
    task="""A chart is in `~/ckaquest-work/128/webapp/`.

Install it as release **monitoring-stack** in namespace **monitoring** (it does not exist yet), with:
- `replicaCount` **3**
- `service.type` **NodePort**

All 3 pods must be Running.""",
    docs=["https://helm.sh/docs/helm/helm_install/", "https://helm.sh/docs/chart_template_guide/values_files/"]),
    setup=r"""helm uninstall monitoring-stack -n monitoring >/dev/null 2>&1
kubectl delete ns monitoring --ignore-not-found --wait=true >/dev/null 2>&1
W="$(cq_work_dir 128)"
[ -e "$W/webapp" ] && mv "$W/webapp" "$W/webapp.old.$(date +%s)"
cp -r "$CQ_ROOT/charts/webapp" "$W/webapp" """,
    validate=r"""check 2 "release monitoring-stack is deployed in monitoring" out_match "deployed" bash -c "helm list -n monitoring | grep '^monitoring-stack'"
check "it runs chart webapp" out_match "webapp-" bash -c "helm list -n monitoring | grep '^monitoring-stack'"
check "values: replicaCount 3, service.type NodePort" out_match '"replicaCount":3.*NodePort|NodePort.*"replicaCount":3' helm get values monitoring-stack -n monitoring -o json
check 2 "3 pods Running" out_eq 3 bash -c "kubectl get pods -n monitoring --field-selector=status.phase=Running --no-headers | wc -l"
check "the Service is NodePort" out_match NodePort kubectl get svc -n monitoring -o jsonpath='{.items[*].spec.type}'""",
    solve=r"""helm install monitoring-stack "$CQ_WORK/128/webapp" -n monitoring --create-namespace --set replicaCount=3 --set service.type=NodePort
kubectl rollout status deploy -n monitoring --timeout=120s""",
    cleanup="""helm uninstall monitoring-stack -n monitoring >/dev/null 2>&1
kubectl delete ns monitoring --ignore-not-found --wait=false >/dev/null 2>&1""",
    hints=["`helm install <release> <path to chart dir>` works without a repo.",
           "`cat ~/ckaquest-work/128/webapp/values.yaml` shows the keys to set.",
           "`helm install monitoring-stack ~/ckaquest-work/128/webapp -n monitoring --create-namespace --set replicaCount=3 --set service.type=NodePort`"],
    solution="""```bash
cat ~/ckaquest-work/128/webapp/values.yaml
helm install monitoring-stack ~/ckaquest-work/128/webapp -n monitoring --create-namespace \\
  --set replicaCount=3 --set service.type=NodePort
helm list -n monitoring
k get pods,svc -n monitoring
```""",
    debrief="""# A Chart on Disk

## What happened
A chart can come from a repo (`repo/chart`), an archive (`chart.tgz`), a URL or a plain directory. Helm reads `Chart.yaml`, `values.yaml` and `templates/` the same way.

`-n` only picks the namespace. If it does not exist, the install fails unless you add `--create-namespace`.

## Overrides
- `--set a.b=c`: one value, nested with dots.
- `-f my-values.yaml`: many values. Later files win.
- `helm get values <release>`: what you set. Add `-a` for everything.

## Exam angle
- Read `values.yaml` for the exact key names. `replica_count` and `replicaCount` are different keys, and a wrong one is ignored without an error.

Bookmark: https://helm.sh/docs/helm/helm_install/

Your notes: Helm Basics""")
