"""Writes World 13 (curriculum gaps: HA control plane, cri-dockerd, anti-affinity, topology spread,
volume expansion, runtime and plugin inspection)."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
from genlib import level

W = "world-13-loose-ends"
STAGE = '"$CQ_ROOT/cluster/stages.sh"'
BARE_DOWN = '"$CQ_ROOT/bin/cq-cluster" bare-down >/dev/null 2>&1'
BARE_NOTE = """

The bare nodes are **bare-controlplane** and **bare-node01** (`ssh bare-controlplane`). They are separate from the game cluster. Your normal kubectl does not talk to them."""
HA_DOCS = "https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/high-availability/"
SCHED_DOCS = "https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/"
SPREAD_DOCS = "https://kubernetes.io/docs/concepts/scheduling-eviction/topology-spread-constraints/"

level(W, "level-111-ha-control-plane", dict(
    name="Room for More Control Planes",
    description="The first control plane must be ready for two more to join later",
    objective="Init a cluster behind a stable endpoint and produce the control plane join command",
    xp=400, difficulty="advanced", expected_time="12m", domain="architecture", course_section=10,
    namespace="lifecycle", context="bare-controlplane",
    concepts=["HA control plane", "controlPlaneEndpoint", "upload-certs", "certificate key"],
    task="""The team wants a highly available control plane later. The first node must be set up so more control plane nodes can join.

On **bare-controlplane**:
- make the name `k8s-api.ckaquest.local` resolve to the node's own IPv4 address (use `/etc/hosts`)
- create the cluster with kubeadm. Control plane endpoint **k8s-api.ckaquest.local:6443**, pod network CIDR **10.50.0.0/16**. Upload the control plane certificates to the cluster
- set up `/root/.kube/config` for root
- write the full command that joins **another control plane node** to `/root/cp-join.sh`

Do not install a CNI.""" + BARE_NOTE,
    docs=[HA_DOCS, "https://kubernetes.io/docs/reference/setup-tools/kubeadm/kubeadm-init/"]),
    setup=STAGE + " bare fresh",
    validate=r"""K='kubectl --kubeconfig /etc/kubernetes/admin.conf'
check "k8s-api.ckaquest.local is in /etc/hosts" node_ok bare-controlplane 'grep -Eq "^[0-9.]+[[:space:]]+k8s-api.ckaquest.local" /etc/hosts'
check "API server answers" node_ok bare-controlplane "$K get --raw=/readyz"
check 2 "controlPlaneEndpoint is k8s-api.ckaquest.local:6443" node_ok bare-controlplane "$K -n kube-system get cm kubeadm-config -o yaml | grep -q 'controlPlaneEndpoint: k8s-api.ckaquest.local:6443'"
check "podSubnet is 10.50.0.0/16" node_ok bare-controlplane "$K -n kube-system get cm kubeadm-config -o yaml | grep -q 'podSubnet: 10.50.0.0/16'"
check 2 "control plane certificates are uploaded (secret kubeadm-certs)" node_ok bare-controlplane "$K -n kube-system get secret kubeadm-certs"
check "admin.conf points at the endpoint, not the node IP" node_ok bare-controlplane 'grep -q "server: https://k8s-api.ckaquest.local:6443" /etc/kubernetes/admin.conf'
check "kubectl works for root without flags" node_ok bare-controlplane 'kubectl get nodes'
check 2 "cp-join.sh joins a control plane through the endpoint" node_ok bare-controlplane 'f=/root/cp-join.sh; grep -q "kubeadm join k8s-api.ckaquest.local:6443" $f && grep -q -- "--control-plane" $f && grep -Eq -- "--certificate-key [0-9a-f]{64}" $f && grep -q -- "--discovery-token-ca-cert-hash sha256:" $f'""",
    solve=r"""ip="$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}} {{end}}' "$(cq_node_name bare-controlplane)" | awk '{print $1}')"
cq_node_sh bare-controlplane "echo '$ip k8s-api.ckaquest.local' >> /etc/hosts
kubeadm init --control-plane-endpoint=k8s-api.ckaquest.local:6443 --pod-network-cidr=10.50.0.0/16 --upload-certs >/root/kubeadm-init.log 2>&1
mkdir -p /root/.kube && cp /etc/kubernetes/admin.conf /root/.kube/config
key=\$(kubeadm init phase upload-certs --upload-certs 2>/dev/null | tail -1)
kubeadm token create --print-join-command --certificate-key \$key > /root/cp-join.sh"
""",
    cleanup=BARE_DOWN,
    hints=["Get the IPv4 address with `ip -4 addr show eth0`. The endpoint must resolve before `kubeadm init` runs.",
           "`kubeadm init --help`: look for `--control-plane-endpoint` and `--upload-certs`. The init output prints two join commands. The one with `--control-plane` is for control plane nodes.",
           "The certificate key in the init output is easy to lose. `kubeadm init phase upload-certs --upload-certs` prints a fresh one, and `kubeadm token create --print-join-command --certificate-key <key>` builds the whole command."],
    solution="""```bash
ssh bare-controlplane
ip -4 addr show eth0                                   # say 172.19.0.5
echo "172.19.0.5 k8s-api.ckaquest.local" >> /etc/hosts
kubeadm init --control-plane-endpoint=k8s-api.ckaquest.local:6443 \\
  --pod-network-cidr=10.50.0.0/16 --upload-certs
mkdir -p ~/.kube && cp /etc/kubernetes/admin.conf ~/.kube/config

# copy the control plane join command from the output, or build it again:
KEY=$(kubeadm init phase upload-certs --upload-certs | tail -1)
kubeadm token create --print-join-command --certificate-key $KEY > /root/cp-join.sh
```""",
    debrief="""# Room for More Control Planes

## What happened
A highly available control plane is several control plane nodes behind one stable address. In production that address is a load balancer or a virtual IP. Here it is a name in `/etc/hosts`.

`--control-plane-endpoint` writes that name into every kubeconfig and into the API server certificate. You cannot add it later without regenerating certificates. That is why it has to be there from the first `kubeadm init`.

`--upload-certs` puts the CA and other shared keys into the Secret `kubeadm-certs`, encrypted with the certificate key. A joining control plane node downloads them with `--certificate-key`. The Secret is deleted after 2 hours. `kubeadm init phase upload-certs --upload-certs` uploads them again with a new key.

## Two join commands
- Worker: `kubeadm join <endpoint> --token ... --discovery-token-ca-cert-hash ...`
- Control plane: the same plus `--control-plane --certificate-key <key>`

## Stacked or external etcd
- Stacked: etcd runs on each control plane node. This is the kubeadm default. Use 3 control plane nodes for quorum.
- External: etcd runs on its own hosts. You need more machines, but losing a control plane node does not cost an etcd member.

## Exam angle
- The exam cannot give you three machines and a load balancer. Expect questions about the flags, the join command and the endpoint.
- Search "high availability" in the docs. The kubeadm HA page has every command.

Bookmark: https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/high-availability/

Your notes: Cluster Install (course sections 10 and 11)""")

level(W, "level-112-cri-dockerd", dict(
    name="Another Runtime Socket",
    description="A node must run Docker workloads through cri-dockerd",
    objective="Install a .deb, start its service and set the kernel parameters",
    xp=300, difficulty="intermediate", expected_time="8m", domain="architecture", course_section=10,
    namespace="lifecycle", context="bare-node01",
    concepts=["CRI", "cri-dockerd", "dpkg", "systemctl", "sysctl"],
    task="""On **bare-node01** the package `/root/pkgs/cri-dockerd_0.3.20-ckaquest_all.deb` is ready.
- install it with dpkg
- enable and start its service **cri-docker** so it also starts after a reboot
- set these kernel parameters now and persistently in a file under `/etc/sysctl.d/`:
  - `net.ipv4.ip_forward = 1`
  - `net.ipv6.conf.all.forwarding = 1`

This package is a CKAQuest practice copy. It has the same name, service and socket path as the real cri-dockerd but does not need Docker.""" + BARE_NOTE,
    docs=["https://kubernetes.io/docs/setup/production-environment/container-runtimes/",
          "https://kubernetes.io/docs/tasks/administer-cluster/sysctl-cluster/"]),
    setup=STAGE + r""" bare fresh
cq_node_sh bare-node01 'set -e
d=/root/.cq-build/cri-dockerd
mkdir -p $d/DEBIAN $d/usr/bin $d/lib/systemd/system /root/pkgs
cat > $d/DEBIAN/control <<EOF
Package: cri-dockerd
Version: 0.3.20-ckaquest
Architecture: all
Maintainer: CKAQuest
Description: CKAQuest practice package that stands in for cri-dockerd
EOF
cat > $d/usr/bin/cri-dockerd <<"EOF"
#!/bin/sh
# Practice stand-in. It only holds the socket path the real cri-dockerd serves.
rm -f /run/cri-dockerd.sock
touch /run/cri-dockerd.sock
exec sleep infinity
EOF
chmod 755 $d/usr/bin/cri-dockerd
cat > $d/lib/systemd/system/cri-docker.service <<EOF
[Unit]
Description=CRI interface for Docker (CKAQuest practice package)

[Service]
ExecStart=/usr/bin/cri-dockerd
Restart=always

[Install]
WantedBy=multi-user.target
EOF
dpkg-deb --build $d /root/pkgs/cri-dockerd_0.3.20-ckaquest_all.deb >/dev/null
sysctl -qw net.ipv4.ip_forward=0 net.ipv6.conf.all.forwarding=0'""",
    validate=r"""check 2 "package cri-dockerd is installed" node_ok bare-node01 'dpkg-query -W -f="\${Status}" cri-dockerd 2>/dev/null | grep -q "install ok installed"'
check "service cri-docker is enabled" node_ok bare-node01 '[ "$(systemctl is-enabled cri-docker)" = enabled ]'
check 2 "service cri-docker is running" node_ok bare-node01 'systemctl is-active -q cri-docker && test -e /run/cri-dockerd.sock'
check "ip_forward = 1 in /etc/sysctl.d" node_ok bare-node01 'cat /etc/sysctl.d/*.conf | grep -Eq "^net.ipv4.ip_forward *= *1"'
check "ipv6 forwarding = 1 in /etc/sysctl.d" node_ok bare-node01 'cat /etc/sysctl.d/*.conf | grep -Eq "^net.ipv6.conf.all.forwarding *= *1"'
check 2 "both are 1 right now" node_ok bare-node01 '[ "$(sysctl -n net.ipv4.ip_forward)$(sysctl -n net.ipv6.conf.all.forwarding)" = 11 ]'""",
    solve=r"""cq_node_sh bare-node01 'dpkg -i /root/pkgs/cri-dockerd_0.3.20-ckaquest_all.deb >/dev/null
systemctl daemon-reload
systemctl enable --now cri-docker
printf "net.ipv4.ip_forward = 1\nnet.ipv6.conf.all.forwarding = 1\n" > /etc/sysctl.d/99-cri.conf
sysctl --system >/dev/null 2>&1; true'""",
    cleanup=BARE_DOWN,
    hints=["`dpkg -i <file>` installs a local .deb. `dpkg -L cri-dockerd` lists what it installed, including the unit file.",
           "`systemctl enable --now <service>` does enable and start in one step.",
           "Write both lines to a new file like `/etc/sysctl.d/99-cri.conf`, then `sysctl --system`."],
    solution="""```bash
ssh bare-node01
dpkg -i /root/pkgs/cri-dockerd_0.3.20-ckaquest_all.deb
systemctl enable --now cri-docker
systemctl status cri-docker
cat <<EOF > /etc/sysctl.d/99-cri.conf
net.ipv4.ip_forward = 1
net.ipv6.conf.all.forwarding = 1
EOF
sysctl --system
sysctl net.ipv4.ip_forward net.ipv6.conf.all.forwarding
```""",
    debrief="""# Another Runtime Socket

## What happened
The kubelet talks to a container runtime through the CRI, a gRPC API on a Unix socket. containerd and CRI-O speak CRI directly. Docker Engine does not, so since dockershim was removed in v1.24, Docker needs the adapter cri-dockerd. It serves `unix:///run/cri-dockerd.sock`.

A node uses it when the kubelet points there: `kubeadm init/join --cri-socket unix:///run/cri-dockerd.sock`, or `containerRuntimeEndpoint` in the kubelet config.

## The three steps
- `dpkg -i` installs. `dpkg -l | grep cri` and `dpkg -L <pkg>` check.
- `systemctl enable --now` makes the service start now and after a reboot. `enable` alone does not start it.
- `/etc/sysctl.d/*.conf` plus `sysctl --system` makes kernel settings both persistent and live.

## Exam angle
- People report this exact shape: install cri-dockerd from a .deb, start it, set sysctls. The values are given in the task.
- Check every part afterwards: `systemctl is-enabled`, `systemctl is-active`, `sysctl <key>`.

Bookmark: https://kubernetes.io/docs/setup/production-environment/container-runtimes/

Your notes: Cluster Install (course sections 10 and 11)""")

level(W, "level-113-anti-affinity", dict(
    name="Never on the Same Node",
    description="Two cache pods on one node means one node failure takes both",
    objective="Spread a Deployment with required pod anti-affinity",
    xp=300, difficulty="intermediate", expected_time="8m", domain="workloads", course_section=3,
    namespace="anti-lab", concepts=["podAntiAffinity", "topologyKey", "rolling update and anti-affinity"],
    task="""Deployment **cache** in namespace **anti-lab** runs 2 pods with label `app=cache`.

Change it so that **no two cache pods can ever run on the same node** (a hard rule, by hostname). Then scale it to **3** replicas.

The cluster has 2 worker nodes, so one pod will stay Pending. That is expected. All 3 pods must come from the updated pod template.""",
    docs=[SCHED_DOCS + "#inter-pod-affinity-and-anti-affinity"]),
    setup="""kubectl create deployment cache -n anti-lab --image=nginx:1.27 --replicas=2 >/dev/null
kubectl rollout status deploy/cache -n anti-lab --timeout=120s >/dev/null 2>&1 || true""",
    validate=r"""A='{.spec.template.spec.affinity.podAntiAffinity.requiredDuringSchedulingIgnoredDuringExecution[0]'
running_nodes() { kubectl get pods -n anti-lab -l app=cache -o jsonpath='{range .items[?(@.status.phase=="Running")]}{.spec.nodeName}{"\n"}{end}'; }
two_nodes() { [ "$(running_nodes | wc -l)" = 2 ] && [ "$(running_nodes | sort -u | wc -l)" = 2 ]; }
one_pending() { [ "$(kubectl get pods -n anti-lab -l app=cache --field-selector=status.phase=Pending --no-headers 2>/dev/null | wc -l)" = 1 ]; }
check 2 "required anti-affinity with topologyKey kubernetes.io/hostname" field_eq anti-lab deploy/cache "$A.topologyKey}" kubernetes.io/hostname
check "the rule selects the cache pods" field_match anti-lab deploy/cache "$A.labelSelector}" cache
check "3 replicas, all from the updated template" field_eq anti-lab deploy/cache '{.spec.replicas}/{.status.updatedReplicas}' 3/3
check 2 "2 cache pods Running, on different nodes" two_nodes
check "the third pod is Pending" one_pending""",
    solve=r"""kubectl scale deploy cache -n anti-lab --replicas=0 >/dev/null
kubectl patch deploy cache -n anti-lab --type merge -p '{"spec":{"replicas":3,"template":{"spec":{"affinity":{"podAntiAffinity":{"requiredDuringSchedulingIgnoredDuringExecution":[{"labelSelector":{"matchLabels":{"app":"cache"}},"topologyKey":"kubernetes.io/hostname"}]}}}}}}' >/dev/null
settled() { [ "$(kubectl get deploy cache -n anti-lab -o jsonpath='{.status.readyReplicas}/{.status.updatedReplicas}')" = 2/3 ] \
  && [ "$(kubectl get pods -n anti-lab -l app=cache --no-headers | wc -l)" = 3 ]; }
cq_wait 120 settled""",
    hints=["`k explain deploy.spec.template.spec.affinity.podAntiAffinity`. You want the `requiredDuringScheduling...` list.",
           "Each entry needs a `labelSelector` that matches the cache pods and `topologyKey: kubernetes.io/hostname`.",
           "If the rollout hangs: the new pods refuse nodes where old cache pods still run, and the old pods wait for the new ones. Scale to 0 first, or delete the old pods."],
    solution="""```yaml
spec:
  replicas: 3
  template:
    spec:
      affinity:
        podAntiAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
          - labelSelector:
              matchLabels:
                app: cache
            topologyKey: kubernetes.io/hostname
```

```bash
k scale deploy cache -n anti-lab --replicas=0
k edit deploy cache -n anti-lab        # add the block above, replicas 3
k get pods -n anti-lab -o wide         # 2 Running on different nodes, 1 Pending
k describe pod <pending pod> -n anti-lab   # didn't match pod anti-affinity rules
```""",
    debrief="""# Never on the Same Node

## What happened
Pod anti-affinity looks at the pods already on a node. `topologyKey: kubernetes.io/hostname` makes every node its own domain. So a node with one cache pod refuses a second one. With 2 workers the third pod has nowhere to go. That Pending pod is proof the rule works.

## The rollout trap
The label `app=cache` also matches the old pods. During a rolling update the new pod is not allowed next to an old one, and the old ones are not removed until new ones are ready. The rollout hangs. Ways out:
- scale to 0 first, or delete the old pods
- `strategy: Recreate`
- `maxUnavailable: 1` so an old pod can go first

## Required or preferred
- `requiredDuringScheduling...`: hard rule. Pods stay Pending.
- `preferredDuringScheduling...` with a `weight`: soft rule. The scheduler tries, but packs pods together if it must.
- `podAffinity` is the opposite: run next to matching pods.

## Exam angle
- "One pod per node" can mean anti-affinity, or a DaemonSet if every node needs one. Read the task.
- Copy the block from the docs page "Assigning Pods to Nodes".

Bookmark: https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/

Your notes: Scheduling""")

level(W, "level-114-topology-spread", dict(
    name="Even Across Zones",
    description="All api pods pile up in one zone",
    objective="Label nodes with zones and add a hard topology spread constraint",
    xp=300, difficulty="intermediate", expected_time="10m", domain="workloads", course_section=3,
    namespace="spread-lab", concepts=["topologySpreadConstraints", "maxSkew", "zone labels", "matchLabelKeys"],
    task="""Deployment **api** in namespace **spread-lab** runs 4 pods (`app=api`). They all land on node01.

1. Label node **node01** with `topology.kubernetes.io/zone=zone-a` and node **node02** with `topology.kubernetes.io/zone=zone-b`.
2. Add a topology spread constraint to **api**: spread by `topology.kubernetes.io/zone`, `maxSkew` 1, and do **not** schedule pods that would break it.

Keep the existing node affinity and the 4 replicas. In the end each zone must run 2 api pods.""",
    docs=[SPREAD_DOCS, "https://kubernetes.io/docs/reference/labels-annotations-taints/#topologykubernetesiozone"]),
    setup=r"""for n in node01 node02; do kubectl label node "$(cq_node_name $n)" topology.kubernetes.io/zone- >/dev/null 2>&1; done
cat <<EOF | kubectl apply -f - >/dev/null
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
  namespace: spread-lab
spec:
  replicas: 4
  selector:
    matchLabels:
      app: api
  template:
    metadata:
      labels:
        app: api
    spec:
      affinity:
        nodeAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            preference:
              matchExpressions:
              - key: kubernetes.io/hostname
                operator: In
                values: ["$(cq_node_name node01)"]
      containers:
      - name: api
        image: nginx:1.27
EOF
kubectl rollout status deploy/api -n spread-lab --timeout=120s >/dev/null 2>&1 || true""",
    validate=r"""N1="$(cq_node_name node01)"; N2="$(cq_node_name node02)"
T='{.spec.template.spec.topologySpreadConstraints[0]'
per_node() { kubectl get pods -n spread-lab -l app=api -o jsonpath='{range .items[?(@.status.phase=="Running")]}{.spec.nodeName} {.metadata.deletionTimestamp}{"\n"}{end}' | awk 'NF==1{print $1}' | grep -cx "$1"; }
two_each() { [ "$(per_node "$N1")" = 2 ] && [ "$(per_node "$N2")" = 2 ]; }
check "node01 is in zone-a" field_eq - node/$N1 '{.metadata.labels.topology\.kubernetes\.io/zone}' zone-a
check "node02 is in zone-b" field_eq - node/$N2 '{.metadata.labels.topology\.kubernetes\.io/zone}' zone-b
check 2 "spread by zone with maxSkew 1" field_eq spread-lab deploy/api "$T.topologyKey}/$T.maxSkew}" topology.kubernetes.io/zone/1
check "whenUnsatisfiable is DoNotSchedule" field_eq spread-lab deploy/api "$T.whenUnsatisfiable}" DoNotSchedule
check "the constraint selects the api pods" field_match spread-lab deploy/api "$T.labelSelector}" api
check "node affinity is still there" field_match spread-lab deploy/api '{.spec.template.spec.affinity.nodeAffinity}' preferred
check "4 replicas ready" field_eq spread-lab deploy/api '{.spec.replicas}/{.status.readyReplicas}/{.status.updatedReplicas}' 4/4/4
check 2 "2 api pods in each zone" two_each""",
    solve=r"""kubectl label node "$(cq_node_name node01)" topology.kubernetes.io/zone=zone-a --overwrite >/dev/null
kubectl label node "$(cq_node_name node02)" topology.kubernetes.io/zone=zone-b --overwrite >/dev/null
kubectl patch deploy api -n spread-lab --type merge -p '{"spec":{"template":{"spec":{"topologySpreadConstraints":[{"maxSkew":1,"topologyKey":"topology.kubernetes.io/zone","whenUnsatisfiable":"DoNotSchedule","labelSelector":{"matchLabels":{"app":"api"}},"matchLabelKeys":["pod-template-hash"]}]}}}}' >/dev/null
kubectl rollout status deploy/api -n spread-lab --timeout=120s >/dev/null
gone() { [ "$(kubectl get pods -n spread-lab -l app=api --no-headers | wc -l)" = 4 ]; }
cq_wait 90 gone""",
    cleanup="""for n in node01 node02; do kubectl label node "$(cq_node_name $n)" topology.kubernetes.io/zone- >/dev/null 2>&1; done""",
    hints=["`k label node <name> key=value`. Find the real node names with `k get nodes`.",
           "`k explain deploy.spec.template.spec.topologySpreadConstraints`. You need maxSkew, topologyKey, whenUnsatisfiable and labelSelector.",
           "If the spread ends 3 and 1 after the rollout, the old pods were counted while the new ones were placed. Add `matchLabelKeys: [pod-template-hash]` so only pods of the same version count, then `k rollout restart`."],
    solution="""```bash
k label node node01 topology.kubernetes.io/zone=zone-a     # use the real node names
k label node node02 topology.kubernetes.io/zone=zone-b
k edit deploy api -n spread-lab
```

```yaml
spec:
  template:
    spec:
      topologySpreadConstraints:
      - maxSkew: 1
        topologyKey: topology.kubernetes.io/zone
        whenUnsatisfiable: DoNotSchedule
        labelSelector:
          matchLabels:
            app: api
        matchLabelKeys:
        - pod-template-hash
```

```bash
k get pods -n spread-lab -o wide        # 2 per node
```""",
    debrief="""# Even Across Zones

## What happened
A topology domain is every node with the same value of a label. `maxSkew: 1` means the pod count in the fullest and the emptiest domain may differ by at most 1. `DoNotSchedule` makes it a hard filter, so it beats the preferred node affinity, which only adds points.

Without zone labels the nodes are not in any domain. Real cloud nodes get `topology.kubernetes.io/zone` from the cloud provider. Here you set it yourself.

## The rollout detail
The scheduler only checks the spread when it places a pod. During a rolling update the old pods still count, so the final spread can end up uneven. `matchLabelKeys: [pod-template-hash]` limits the count to pods of the same ReplicaSet.

## Spread, anti-affinity or DaemonSet
- Anti-affinity: at most one per domain.
- Topology spread: as even as possible, many per domain allowed.
- DaemonSet: exactly one per node.

## Exam angle
- The docs page "Pod Topology Spread Constraints" has a full example.
- Check with `k get pods -o wide` and count per node.

Bookmark: https://kubernetes.io/docs/concepts/scheduling-eviction/topology-spread-constraints/

Your notes: Scheduling""")

level(W, "level-115-volume-expansion", dict(
    name="The Disk Is Too Small",
    description="The database needs more space, but the API says no",
    objective="Expand a bound PVC without recreating it",
    xp=250, difficulty="intermediate", expected_time="6m", domain="storage", course_section=8,
    namespace="grow-lab", concepts=["volume expansion", "allowVolumeExpansion", "PVC resize"],
    task="""PVC **data** in namespace **grow-lab** requests 1Gi and is used by pod **db**. It must request **2Gi**.

Do not delete or recreate the PVC or the pod. If the API refuses the change, find out why and fix the cause.""",
    docs=["https://kubernetes.io/docs/concepts/storage/persistent-volumes/#expanding-persistent-volumes-claims",
          "https://kubernetes.io/docs/concepts/storage/storage-classes/#allow-volume-expansion"]),
    setup=r"""kubectl delete sc slow-local --ignore-not-found >/dev/null 2>&1
cat <<'EOF' | kubectl apply -f - >/dev/null
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: slow-local
provisioner: rancher.io/local-path
reclaimPolicy: Delete
volumeBindingMode: WaitForFirstConsumer
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: data
  namespace: grow-lab
spec:
  accessModes: ["ReadWriteOnce"]
  storageClassName: slow-local
  resources:
    requests:
      storage: 1Gi
---
apiVersion: v1
kind: Pod
metadata:
  name: db
  namespace: grow-lab
spec:
  containers:
  - name: db
    image: busybox:1.36
    command: ["sh", "-c", "echo rows > /data/table; sleep 3600"]
    volumeMounts:
    - name: data
      mountPath: /data
  volumes:
  - name: data
    persistentVolumeClaim:
      claimName: data
EOF
kubectl wait --for=condition=Ready pod/db -n grow-lab --timeout=120s >/dev/null 2>&1 || true
kubectl create configmap original -n grow-lab \
  --from-literal=pvc="$(kubectl get pvc data -n grow-lab -o jsonpath='{.metadata.uid}')" \
  --from-literal=pod="$(kubectl get pod db -n grow-lab -o jsonpath='{.metadata.uid}')" >/dev/null""",
    validate=r"""same_uid() { [ -n "$(jp grow-lab cm/original "{.data.$1}")" ] && [ "$(jp grow-lab "$2" '{.metadata.uid}')" = "$(jp grow-lab cm/original "{.data.$1}")" ]; }
check 2 "StorageClass slow-local allows volume expansion" field_eq - sc/slow-local '{.allowVolumeExpansion}' true
check 2 "PVC data requests 2Gi" field_eq grow-lab pvc/data '{.spec.resources.requests.storage}' 2Gi
check "it is the same PVC as before" same_uid pvc pvc/data
check "pod db was not recreated and is Running" same_uid pod pod/db
check "pod db is Running" pod_running grow-lab db""",
    solve="""kubectl patch sc slow-local -p '{"allowVolumeExpansion":true}' >/dev/null
kubectl patch pvc data -n grow-lab -p '{"spec":{"resources":{"requests":{"storage":"2Gi"}}}}' >/dev/null""",
    cleanup="kubectl delete sc slow-local --ignore-not-found >/dev/null 2>&1",
    hints=["Try `k edit pvc data -n grow-lab` and read the error carefully. It names the object at fault.",
           "Expansion is allowed per StorageClass. `k get sc` has a column for it.",
           "`allowVolumeExpansion` can be changed on an existing StorageClass. Set it to true, then edit the PVC again."],
    solution="""```bash
k patch sc slow-local -p '{"allowVolumeExpansion": true}'
k patch pvc data -n grow-lab -p '{"spec":{"resources":{"requests":{"storage":"2Gi"}}}}'
k get pvc data -n grow-lab
```""",
    debrief="""# The Disk Is Too Small

## What happened
The API refused the bigger request: "only dynamically provisioned pvc can be resized and the storageclass that provisions the pvc must support resize". The StorageClass decides, through `allowVolumeExpansion: true`. It is one of the few StorageClass fields you can change after creation.

## What happens next on a real driver
1. You raise `spec.resources.requests.storage` on the PVC. You can only grow it, never shrink it.
2. The CSI external-resizer grows the volume in the storage backend.
3. The kubelet grows the filesystem. Some drivers need the pod restarted for that step. The PVC then shows the condition `FileSystemResizePending`.
4. `status.capacity` shows the new size.

The local-path provisioner in this cluster cannot resize anything. So here `status.capacity` stays 1Gi while the request is 2Gi. The API part, which the exam checks, is done.

## Exam angle
- "Expand the PVC" means edit the PVC, not the PV.
- If it is refused, check `allowVolumeExpansion` on the StorageClass.
- `k get pvc` CAPACITY shows status, not the request. Check the spec with `-o yaml`.

Bookmark: https://kubernetes.io/docs/concepts/storage/persistent-volumes/#expanding-persistent-volumes-claims

Your notes: Storage""")

level(W, "level-116-plugin-inspection", dict(
    name="What Runs Under the Hood",
    description="Find out which runtime, network plugin and storage drivers a node uses",
    objective="Read CRI, CNI and CSI details from a node and the API",
    xp=250, difficulty="intermediate", expected_time="8m", domain="architecture", course_section=10,
    namespace="plugin-lab", concepts=["CRI", "CNI", "CSI", "kubelet config"],
    task="""Write the answers about node **node01** to `~/ckaquest-work/116/answers.txt`, one `key=value` per line with no spaces:

- `cri_endpoint`: the container runtime endpoint the kubelet on node01 uses
- `runtime`: the container runtime and version node01 reports, exactly as the API shows it
- `cni_config`: the file name (not the path) of the CNI config on node01
- `cni_plugin`: the `type` of the first plugin in that CNI config
- `pod_cidr`: the pod CIDR assigned to node01
- `csi_drivers`: how many CSIDriver objects the cluster has""",
    docs=["https://kubernetes.io/docs/concepts/extend-kubernetes/compute-storage-net/network-plugins/",
          "https://kubernetes.io/docs/reference/config-api/kubelet-config.v1beta1/"]),
    setup=r"""W="$(cq_work_dir 116)"; [ -e "$W/answers.txt" ] && mv -f "$W/answers.txt" "$W/answers.txt.old"; true""",
    validate=r"""N="$(cq_node_name node01)"
ans() { grep -E "^$1=" "$CQ_WORK/116/answers.txt" 2>/dev/null | head -1 | cut -d= -f2- | tr -d ' \r'; }
E_CRI="$(cq_node_sh node01 'sed -n "s/^containerRuntimeEndpoint: *//p" /var/lib/kubelet/config.yaml')"
E_CNI="$(cq_node_sh node01 'ls /etc/cni/net.d | grep -E "\.conf(list)?$" | sort | head -1')"
E_PLUGIN="$(cq_node_sh node01 "grep -m1 '\"type\"' /etc/cni/net.d/$E_CNI" | sed -E 's/.*"type": *"([^"]+)".*/\1/')"
E_RT="$(kubectl get node "$N" -o jsonpath='{.status.nodeInfo.containerRuntimeVersion}')"
E_CIDR="$(kubectl get node "$N" -o jsonpath='{.spec.podCIDR}')"
E_CSI="$(kubectl get csidriver --no-headers 2>/dev/null | wc -l)"
check "answers.txt exists" file_exists "$CQ_WORK/116/answers.txt"
check "cri_endpoint is right" out_eq "$E_CRI" ans cri_endpoint
check "runtime is right" out_eq "$E_RT" ans runtime
check "cni_config is right" out_eq "$E_CNI" ans cni_config
check "cni_plugin is right" out_eq "$E_PLUGIN" ans cni_plugin
check "pod_cidr is right" out_eq "$E_CIDR" ans pod_cidr
check "csi_drivers is right" out_eq "$E_CSI" ans csi_drivers""",
    solve=r"""N="$(cq_node_name node01)"
cni="$(cq_node_sh node01 'ls /etc/cni/net.d | grep -E "\.conf(list)?$" | sort | head -1')"
{
echo "cri_endpoint=$(cq_node_sh node01 'sed -n "s/^containerRuntimeEndpoint: *//p" /var/lib/kubelet/config.yaml')"
echo "runtime=$(kubectl get node "$N" -o jsonpath='{.status.nodeInfo.containerRuntimeVersion}')"
echo "cni_config=$cni"
echo "cni_plugin=$(cq_node_sh node01 "grep -m1 '\"type\"' /etc/cni/net.d/$cni" | sed -E 's/.*"type": *"([^"]+)".*/\1/')"
echo "pod_cidr=$(kubectl get node "$N" -o jsonpath='{.spec.podCIDR}')"
echo "csi_drivers=$(kubectl get csidriver --no-headers 2>/dev/null | wc -l)"
} > "$CQ_WORK/116/answers.txt"
""",
    hints=["The kubelet config file is `/var/lib/kubelet/config.yaml` on the node. `ssh node01` first.",
           "CNI configs live in `/etc/cni/net.d`. The plugin binaries live in `/opt/cni/bin`.",
           "`k get node node01 -o wide` shows the runtime. `-o jsonpath='{.spec.podCIDR}'` shows the pod range. `k get csidriver` lists CSI drivers. Zero is a valid answer."],
    solution="""```bash
ssh node01
grep containerRuntimeEndpoint /var/lib/kubelet/config.yaml   # unix:///run/containerd/containerd.sock
ls /etc/cni/net.d                                           # 10-kindnet.conflist
grep -m1 '"type"' /etc/cni/net.d/10-kindnet.conflist        # ptp
exit
k get node node01 -o jsonpath='{.status.nodeInfo.containerRuntimeVersion}{"\\n"}{.spec.podCIDR}{"\\n"}'
k get csidriver --no-headers | wc -l
vi ~/ckaquest-work/116/answers.txt
```""",
    debrief="""# What Runs Under the Hood

## What happened
Kubernetes plugs three things in through standard interfaces:
- **CRI** (container runtime): the kubelet talks gRPC to containerd, CRI-O or cri-dockerd through `containerRuntimeEndpoint`. `crictl` uses the same socket.
- **CNI** (network): the container runtime runs the first config file in `/etc/cni/net.d`, sorted by name, using the binaries in `/opt/cni/bin`. kind uses kindnet with the `ptp` plugin. Calico, Cilium and Flannel drop their own file there.
- **CSI** (storage): drivers register a CSIDriver object and run as pods. This cluster has none, because local-path is an older in-tree style provisioner. That is why expansion and snapshots do not work here.

## Where to look
- Kubelet: `/var/lib/kubelet/config.yaml`, `/var/lib/kubelet/kubeadm-flags.env`, `systemctl cat kubelet`.
- Runtime: `k get nodes -o wide`, `crictl info`.
- Network: `/etc/cni/net.d`, `/opt/cni/bin`, the CNI DaemonSet in kube-system.
- Storage: `k get csidriver`, `k get sc`.

## Exam angle
- The curriculum names CNI, CSI and CRI. Expect "find out and write to a file" questions like this one.
- Answer files are checked as text. No spaces, no extra lines.

Bookmark: https://kubernetes.io/docs/concepts/extend-kubernetes/compute-storage-net/network-plugins/

Your notes: Cluster Architecture""")
