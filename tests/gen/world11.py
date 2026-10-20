"""Writes World 11 (cluster lifecycle on bare nodes and the lab cluster)."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
from genlib import level

W = "world-11-lifecycle"
STAGE = '"$CQ_ROOT/cluster/stages.sh"'
BK = "cq_node_sh bare-controlplane 'kubectl --kubeconfig /etc/kubernetes/admin.conf"
KUBEADM_DOCS = "https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/create-cluster-kubeadm/"
UPGRADE_DOCS = "https://kubernetes.io/docs/tasks/administer-cluster/kubeadm/kubeadm-upgrade/"
BARE_NOTE = """

The bare nodes are **bare-controlplane** and **bare-node01** (`ssh bare-controlplane`). They are separate from the game cluster. Your normal kubectl does not talk to them."""
LAB_NOTE = """

The lab cluster has nodes **lab-controlplane** and **lab-node01** (`ssh lab-controlplane`). The apt repository for Kubernetes v1.37 is already configured on both. On the nodes, kubectl uses the lab cluster. From your terminal use `--context kind-ckaquest-lab`."""

level(W, "level-97-node-prep", dict(
    name="Prepare the Nodes",
    description="Two fresh machines must be ready for kubeadm",
    objective="Load the kernel modules and sysctls Kubernetes needs, persistently",
    xp=250, difficulty="intermediate", expected_time="10m", domain="architecture", course_section=11,
    namespace="lifecycle", context="bare-controlplane, bare-node01",
    concepts=["kernel modules", "sysctl", "container runtime prerequisites"],
    task="""On **both** bare nodes, prepare the OS for Kubernetes so it survives a reboot:
- file `/etc/modules-load.d/k8s.conf` that loads `overlay` and `br_netfilter`
- file `/etc/sysctl.d/k8s.conf` that sets `net.ipv4.ip_forward = 1`, `net.bridge.bridge-nf-call-iptables = 1` and `net.bridge.bridge-nf-call-ip6tables = 1`
- apply the sysctl settings now""" + BARE_NOTE,
    docs=["https://kubernetes.io/docs/setup/production-environment/container-runtimes/#prerequisite-ipv4-forwarding-optional",
          KUBEADM_DOCS]),
    setup=STAGE + " bare fresh\nfor n in bare-controlplane bare-node01; do cq_node_sh $n 'sysctl -qw net.ipv4.ip_forward=0'; done",
    validate="""for n in bare-controlplane bare-node01; do
  check "$n: modules file loads overlay and br_netfilter" node_ok $n 'grep -qx overlay /etc/modules-load.d/k8s.conf && grep -qx br_netfilter /etc/modules-load.d/k8s.conf'
  check "$n: sysctl file has the 3 settings" node_ok $n 'f=/etc/sysctl.d/k8s.conf; grep -Eq "^net.ipv4.ip_forward *= *1" $f && grep -Eq "^net.bridge.bridge-nf-call-iptables *= *1" $f && grep -Eq "^net.bridge.bridge-nf-call-ip6tables *= *1" $f'
  check 2 "$n: ip_forward is 1 now" node_ok $n '[ "$(sysctl -n net.ipv4.ip_forward)" = 1 ]'
done""",
    solve="""for n in bare-controlplane bare-node01; do
cq_node_sh $n 'printf "overlay\\nbr_netfilter\\n" > /etc/modules-load.d/k8s.conf
printf "net.ipv4.ip_forward = 1\\nnet.bridge.bridge-nf-call-iptables = 1\\nnet.bridge.bridge-nf-call-ip6tables = 1\\n" > /etc/sysctl.d/k8s.conf
sysctl --system >/dev/null 2>&1; true'
done""",
    hints=["The container runtime docs page has both files ready to copy.", "`sysctl --system` reads all files in /etc/sysctl.d.",
           "In these container nodes, `modprobe` may fail. That is fine. The files are what the task checks."],
    solution="""```bash
ssh bare-controlplane          # then the same on bare-node01
cat <<EOF > /etc/modules-load.d/k8s.conf
overlay
br_netfilter
EOF
modprobe overlay; modprobe br_netfilter
cat <<EOF > /etc/sysctl.d/k8s.conf
net.ipv4.ip_forward = 1
net.bridge.bridge-nf-call-iptables = 1
net.bridge.bridge-nf-call-ip6tables = 1
EOF
sysctl --system
```""",
    debrief="""# Prepare the Nodes

## What happened
Pods talk across nodes through Linux routing and bridges. `ip_forward` lets the node route packets. `br_netfilter` makes bridged traffic visible to iptables, which kube-proxy needs. `overlay` is the filesystem driver containerd uses.

Files in `/etc/modules-load.d` and `/etc/sysctl.d` make the settings survive a reboot. `modprobe` and `sysctl --system` apply them now.

## Also before kubeadm
- A container runtime with the systemd cgroup driver.
- Swap off, or kubelet configured to tolerate it.
- kubeadm, kubelet, kubectl from pkgs.k8s.io, held with `apt-mark hold`.

## Exam angle
- Node prep is in the curriculum ("prepare underlying infrastructure"). Copy the blocks from the container runtime docs page.

Bookmark: https://kubernetes.io/docs/setup/production-environment/container-runtimes/

Your notes: Cluster Install (course sections 10 and 11)""")

level(W, "level-98-kubeadm-init", dict(
    name="kubeadm init",
    description="Turn bare-controlplane into a control plane",
    objective="Initialise a cluster with kubeadm and a custom pod CIDR",
    xp=350, difficulty="advanced", expected_time="10m", domain="architecture", course_section=11,
    namespace="lifecycle", context="bare-controlplane",
    concepts=["kubeadm init", "pod network CIDR", "admin kubeconfig"],
    task="""On **bare-controlplane**, create a new cluster with kubeadm:
- pod network CIDR **10.50.0.0/16**
- after init, set up `/root/.kube/config` so `kubectl` works for root on that node

Do not install a CNI yet.""" + BARE_NOTE,
    docs=[KUBEADM_DOCS, "https://kubernetes.io/docs/reference/setup-tools/kubeadm/kubeadm-init/"]),
    setup=STAGE + " bare fresh",
    validate="""check 2 "API server on bare-controlplane answers" node_ok bare-controlplane 'kubectl --kubeconfig /etc/kubernetes/admin.conf get --raw=/readyz'
check 2 "podSubnet is 10.50.0.0/16" node_ok bare-controlplane 'kubectl --kubeconfig /etc/kubernetes/admin.conf -n kube-system get cm kubeadm-config -o yaml | grep -q "podSubnet: 10.50.0.0/16"'
check 2 "kubectl works for root without flags" node_ok bare-controlplane 'kubectl get nodes'""",
    solve=STAGE + " bare init",
    hints=["`kubeadm init --help`. One flag sets the pod network range.",
           "Read the end of the init output. It prints the three commands to set up kubectl for your user.",
           "`kubeadm init --pod-network-cidr=10.50.0.0/16`, then `mkdir -p ~/.kube && cp /etc/kubernetes/admin.conf ~/.kube/config`."],
    solution="""```bash
ssh bare-controlplane
kubeadm init --pod-network-cidr=10.50.0.0/16
mkdir -p $HOME/.kube
cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
kubectl get nodes          # NotReady until a CNI is installed
```""",
    debrief="""# kubeadm init

## What happened
`kubeadm init` runs preflight checks, creates the CA and certificates in `/etc/kubernetes/pki`, writes kubeconfigs, writes static pod manifests for etcd, apiserver, controller-manager and scheduler, starts the kubelet, and installs CoreDNS and kube-proxy.

The node stays NotReady until a CNI plugin is installed. CoreDNS stays Pending for the same reason.

## Flags worth knowing
- `--pod-network-cidr`: must match the CNI's pool.
- `--apiserver-advertise-address`: which IP the API server announces.
- `--control-plane-endpoint`: needed for HA later.
- `--kubernetes-version`.
- `--config` takes a ClusterConfiguration file instead of flags.

## Exam angle
- Save the join command from the output. You can always make a new one with `kubeadm token create --print-join-command`.

Bookmark: https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/create-cluster-kubeadm/

Your notes: Cluster Install (course section 11)""")

level(W, "level-99-calico", dict(
    name="Install the CNI",
    description="The new control plane is NotReady because there is no pod network",
    objective="Install Calico with a pool that matches the cluster's pod CIDR",
    xp=350, difficulty="advanced", expected_time="10m", domain="networking", course_section=11,
    namespace="lifecycle", context="bare-controlplane",
    concepts=["CNI", "Calico", "IP pool", "CoreDNS Pending"],
    task="""The cluster on **bare-controlplane** has pod CIDR **10.50.0.0/16** and no CNI. The Calico manifest is at `/root/calico.yaml` on that node.

Install Calico so that its IP pool is **10.50.0.0/16**. The node must become Ready and CoreDNS must run with an IP from that range.""" + BARE_NOTE,
    docs=["https://docs.tigera.io/calico/latest/getting-started/kubernetes/self-managed-onprem/onpremises",
          "https://kubernetes.io/docs/concepts/cluster-administration/addons/"]),
    setup=STAGE + " bare init\n" + """cq_node_sh bare-controlplane "test -s /root/calico.yaml || curl -fsSL -o /root/calico.yaml https://raw.githubusercontent.com/projectcalico/calico/$(grep ^CALICO_VERSION "$CQ_ROOT/cluster/versions.env" | cut -d= -f2)/manifests/calico.yaml\"""",
    validate="""K='kubectl --kubeconfig /etc/kubernetes/admin.conf'
check 2 "Calico IP pool is 10.50.0.0/16" node_ok bare-controlplane "$K get ippools.crd.projectcalico.org default-ipv4-ippool -o jsonpath='{.spec.cidr}' | grep -qx 10.50.0.0/16"
check 2 "bare-controlplane is Ready" node_ok bare-controlplane "$K get node \\$(hostname) --no-headers | grep -q ' Ready'"
check 2 "CoreDNS pods run with 10.50.x.x IPs" node_ok bare-controlplane "$K -n kube-system get pods -l k8s-app=kube-dns -o jsonpath='{.items[*].status.podIP}' | grep -q '^10\\.50\\.'\"""",
    solve=STAGE + " bare cni\nsleep 20",
    hints=["Look for `CALICO_IPV4POOL_CIDR` in /root/calico.yaml. It is commented out.",
           "Uncomment both lines (name and value) and set the value to 10.50.0.0/16. Keep the indentation of the env list.",
           "`kubectl apply -f /root/calico.yaml`, then `kubectl get pods -n kube-system -w`."],
    solution="""```bash
ssh bare-controlplane
vim /root/calico.yaml
#            - name: CALICO_IPV4POOL_CIDR
#              value: "10.50.0.0/16"
kubectl apply -f /root/calico.yaml
kubectl get pods -n kube-system -w
kubectl get nodes
```""",
    debrief="""# Install the CNI

## What happened
Kubernetes does not ship a pod network. The kubelet reports NotReady until a CNI plugin writes its config to `/etc/cni/net.d`. Calico runs as a DaemonSet (calico-node) and assigns pod IPs from its IP pool.

If the pool does not match `--pod-network-cidr`, kube-proxy and the CNI disagree about which IPs are pods. That causes hard-to-find routing problems.

## Exam angle
- Expect "install a CNI that supports NetworkPolicy" or "install from this manifest". Calico and Cilium support policies. Flannel does not.
- With the Tigera operator install, the CIDR lives in the `Installation` resource instead.

Bookmark: https://kubernetes.io/docs/concepts/cluster-administration/addons/

Your notes: CNI, Pod Networking""")

level(W, "level-100-kubeadm-join", dict(
    name="Add a Worker",
    description="bare-node01 must join the new cluster",
    objective="Join a worker node with kubeadm",
    xp=300, difficulty="intermediate", expected_time="8m", domain="architecture", course_section=11,
    namespace="lifecycle", context="bare-controlplane, bare-node01",
    concepts=["kubeadm join", "bootstrap token", "discovery hash"],
    task="""Join **bare-node01** as a worker to the cluster on **bare-controlplane**. Both nodes must be Ready.

Then run a pod **hello** (`nginx:1.27-alpine`) on bare-node01 in that cluster.""" + BARE_NOTE,
    docs=["https://kubernetes.io/docs/reference/setup-tools/kubeadm/kubeadm-join/"]),
    setup=STAGE + " bare cni",
    validate="""K='kubectl --kubeconfig /etc/kubernetes/admin.conf'
W="$(cq_node_name bare-node01)"
check 2 "bare-node01 is a Ready node" node_ok bare-controlplane "$K get node $W --no-headers | grep -q ' Ready'"
check 2 "pod hello runs on bare-node01" node_ok bare-controlplane "[ \\"\\$($K get pod hello -o jsonpath='{.spec.nodeName} {.status.phase}')\\" = '$W Running' ]\"""",
    solve=STAGE + """ bare joined
W="$(cq_node_name bare-node01)"
cq_node_sh bare-controlplane "kubectl --kubeconfig /etc/kubernetes/admin.conf run hello --image=nginx:1.27-alpine --overrides='{\\"spec\\":{\\"nodeName\\":\\"$W\\"}}'"
sleep 30""",
    cleanup='"$CQ_ROOT/bin/cq-cluster" bare-down >/dev/null 2>&1',
    hints=["On the control plane: `kubeadm token create --print-join-command`.", "Run the printed command on bare-node01 as root.",
           "The control plane is tainted, so a plain `kubectl run hello` lands on the worker. Check with `-o wide`."],
    solution="""```bash
ssh bare-controlplane
kubeadm token create --print-join-command
exit
ssh bare-node01
kubeadm join <ip>:6443 --token ... --discovery-token-ca-cert-hash sha256:...
exit
ssh bare-controlplane
kubectl get nodes
kubectl run hello --image=nginx:1.27-alpine
kubectl get pod hello -o wide
```""",
    debrief="""# Add a Worker

## What happened
`kubeadm join` uses the token to authenticate, checks the CA hash, gets a kubelet client certificate through the CSR API (auto-approved for bootstrap tokens), and starts the kubelet. The CNI DaemonSet then lands on the new node and it turns Ready.

You built a whole cluster by hand in this world: node prep, init, CNI, join.

## Exam angle
- If the join token expired, create a new one. Do not re-run `kubeadm init`.
- A failed join leaves files behind. `kubeadm reset` on the worker cleans up before a retry.

Bookmark: https://kubernetes.io/docs/reference/setup-tools/kubeadm/kubeadm-join/

Your notes: Cluster Install (course section 11)""")

level(W, "level-101-upgrade-cp", dict(
    name="Upgrade the Control Plane",
    description="The lab cluster runs v1.36. Move the control plane to v1.37.1.",
    objective="Upgrade the control plane node with kubeadm, the exam way",
    xp=450, difficulty="expert", expected_time="15m", domain="architecture", course_section=6,
    namespace="lifecycle", context="kind-ckaquest-lab",
    concepts=["kubeadm upgrade plan", "kubeadm upgrade apply", "drain", "apt-mark"],
    task="""Upgrade the control plane node **lab-controlplane** from v1.36 to exactly **v1.37.1**: kubeadm, the control plane components, kubelet and kubectl.

Drain the node before you upgrade the kubelet and make it schedulable again afterwards. Do not upgrade lab-node01.""" + LAB_NOTE,
    docs=[UPGRADE_DOCS]),
    setup=STAGE + " lab fresh",
    validate="""C="--context $CQ_LAB_CONTEXT"
CP="$(cq_node_name lab-controlplane)"
check "kubeadm is v1.37.1" node_ok lab-controlplane 'kubeadm version -o short | grep -qx v1.37.1'
check 2 "kube-apiserver runs v1.37.1" out_match "v1.37.1" kubectl $C -n kube-system get pod "kube-apiserver-$CP" -o jsonpath='{.spec.containers[0].image}'
check 2 "kubelet on lab-controlplane is v1.37.1" out_eq v1.37.1 kubectl $C get node "$CP" -o jsonpath='{.status.nodeInfo.kubeletVersion}'
check "lab-controlplane is Ready and schedulable" out_eq "True " sh -c "kubectl $C get node $CP -o jsonpath='{.status.conditions[?(@.type==\\"Ready\\")].status} {.spec.unschedulable}'"
check "lab-node01 was not upgraded" out_match "v1.36" kubectl $C get node "$(cq_node_name lab-node01)" -o jsonpath='{.status.nodeInfo.kubeletVersion}'""",
    solve=STAGE + " lab cp-upgraded",
    hints=["Follow the docs page 'Upgrading kubeadm clusters' top to bottom. Start with `apt-cache madison kubeadm`.",
           "Order: install kubeadm 1.37.1, `kubeadm upgrade plan`, `kubeadm upgrade apply v1.37.1`, drain, install kubelet and kubectl 1.37.1, `systemctl daemon-reload && systemctl restart kubelet`, uncordon.",
           "If packages are held: `apt-mark unhold kubeadm` before and `apt-mark hold kubeadm` after. Here they are not held."],
    solution="""```bash
ssh lab-controlplane
apt-get update
apt-cache madison kubeadm | head -3
apt-get install -y kubeadm='1.37.1-*'
kubeadm version
kubeadm upgrade plan
kubeadm upgrade apply v1.37.1
kubectl drain lab-controlplane --ignore-daemonsets      # use the real node name
apt-get install -y kubelet='1.37.1-*' kubectl='1.37.1-*'
systemctl daemon-reload && systemctl restart kubelet
kubectl uncordon <node>
kubectl get nodes
```""",
    debrief="""# Upgrade the Control Plane

## What happened
kubeadm upgrades in a fixed order: kubeadm itself, then the control plane static pods (`upgrade apply`), then the kubelet on each node. The kubelet may be one minor version behind the API server, never ahead.

`kubeadm upgrade apply` also renews the control plane certificates.

## Rules to remember
- One minor version at a time: 1.36 to 1.37, never 1.35 to 1.37.
- Control plane first, then workers.
- Drain before the kubelet upgrade, uncordon after.
- `kubeadm upgrade apply` only on the first control plane. Other control planes and workers use `kubeadm upgrade node`.

## Exam angle
- The apt version format is `1.37.1-1.1`. Use `apt-cache madison` to see it, or `'1.37.1-*'`.
- The upgrade task is often worth more points and takes 10 minutes. Practice until it is routine.

Bookmark: https://kubernetes.io/docs/tasks/administer-cluster/kubeadm/kubeadm-upgrade/

Your notes: Cluster Upgrade""")

level(W, "level-102-upgrade-worker", dict(
    name="Upgrade the Worker",
    description="The control plane is on v1.37.1. The worker is still on v1.36.",
    objective="Upgrade a worker node with kubeadm upgrade node",
    xp=350, difficulty="advanced", expected_time="10m", domain="architecture", course_section=6,
    namespace="lifecycle", context="kind-ckaquest-lab",
    concepts=["kubeadm upgrade node", "drain from the control plane", "kubelet upgrade"],
    task="""The control plane of the lab cluster runs v1.37.1. Upgrade worker **lab-node01** to **v1.37.1** (kubeadm, kubelet, kubectl).

Drain it first and make it schedulable again at the end.""" + LAB_NOTE,
    docs=["https://kubernetes.io/docs/tasks/administer-cluster/kubeadm/upgrading-linux-nodes/"]),
    setup=STAGE + " lab cp-upgraded",
    validate="""C="--context $CQ_LAB_CONTEXT"
W="$(cq_node_name lab-node01)"
check "kubeadm on lab-node01 is v1.37.1" node_ok lab-node01 'kubeadm version -o short | grep -qx v1.37.1'
check 3 "kubelet on lab-node01 is v1.37.1" out_eq v1.37.1 kubectl $C get node "$W" -o jsonpath='{.status.nodeInfo.kubeletVersion}'
check 2 "lab-node01 is Ready and schedulable" out_eq "True " sh -c "kubectl $C get node $W -o jsonpath='{.status.conditions[?(@.type==\\"Ready\\")].status} {.spec.unschedulable}'\"""",
    solve="""C="--context $CQ_LAB_CONTEXT"
W="$(cq_node_name lab-node01)"
kubectl $C drain "$W" --ignore-daemonsets --delete-emptydir-data
cq_node_sh lab-node01 "apt-get install -y -qq 'kubeadm=1.37.1-*' >/dev/null && kubeadm upgrade node >/dev/null
apt-get install -y -qq 'kubelet=1.37.1-*' 'kubectl=1.37.1-*' >/dev/null
systemctl daemon-reload && systemctl restart kubelet"
sleep 20
kubectl $C uncordon "$W\"""",
    cleanup='"$CQ_ROOT/bin/cq-cluster" lab-down >/dev/null 2>&1',
    hints=["Drain from the control plane (or your terminal with the lab context), not from the worker.",
           "On the worker: install kubeadm 1.37.1, then `kubeadm upgrade node`. Not `apply`.",
           "Then kubelet and kubectl 1.37.1, `systemctl daemon-reload && systemctl restart kubelet`, and uncordon."],
    solution="""```bash
k --context kind-ckaquest-lab drain <worker> --ignore-daemonsets
ssh lab-node01
apt-get update
apt-get install -y kubeadm='1.37.1-*'
kubeadm upgrade node
apt-get install -y kubelet='1.37.1-*' kubectl='1.37.1-*'
systemctl daemon-reload && systemctl restart kubelet
exit
k --context kind-ckaquest-lab uncordon <worker>
```""",
    debrief="""# Upgrade the Worker

## What happened
`kubeadm upgrade node` on a worker only updates the local kubelet config. The real change is the new kubelet binary and its restart.

## Exam angle
- Drain and uncordon run where kubectl has admin access, usually the control plane.
- After `exit` from the worker, check that you are back on the right host before you uncordon.
- A worker can stay one minor version behind for a while, so do the control plane first and the workers one by one.

Bookmark: https://kubernetes.io/docs/tasks/administer-cluster/kubeadm/upgrading-linux-nodes/

Your notes: Cluster Upgrade, Node Maintenance""")
