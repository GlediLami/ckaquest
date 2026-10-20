"""Writes World 7 (cluster admin and security). Run once: venv/bin/python3 tests/gen/world7.py"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
from genlib import level

W = "world-7-admin-security"

level(W, "level-61-csr-user", dict(
    name="A New User Called Jane",
    description="Jane needs a client certificate and read access to pods",
    objective="Sign Jane's CSR through the Kubernetes API and give her read access to pods",
    xp=300, difficulty="intermediate", expected_time="10m", domain="architecture", course_section=7,
    namespace="dev-team", concepts=["CertificateSigningRequest", "kubectl certificate approve", "Role", "RoleBinding"],
    task="""Jane has a private key and a CSR in `~/ckaquest-work/61/` (`jane.key`, `jane.csr`).

1. Create a CertificateSigningRequest called **jane** from `jane.csr`. Use signer `kubernetes.io/kube-apiserver-client` and usage `client auth`.
2. Approve it.
3. Save the issued certificate to `~/ckaquest-work/61/jane.crt` (PEM, not base64).
4. Create a Role **pod-reader** in namespace **dev-team** that allows `get`, `list` and `watch` on pods. Bind it to user **jane** with a RoleBinding **jane-pod-reader**.""",
    docs=["https://kubernetes.io/docs/reference/access-authn-authz/certificate-signing-requests/#normal-user",
          "https://kubernetes.io/docs/reference/access-authn-authz/rbac/"]),
    setup="""W="$(cq_work_dir 61)"
[ -f "$W/jane.key" ] || openssl genrsa -out "$W/jane.key" 2048 2>/dev/null
openssl req -new -key "$W/jane.key" -subj "/CN=jane/O=dev" -out "$W/jane.csr" 2>/dev/null
mv -f "$W/jane.crt" "$W/jane.crt.old" 2>/dev/null || true
kubectl delete csr jane --ignore-not-found >/dev/null""",
    validate="""approved() { kubectl get csr jane -o jsonpath='{.status.conditions[?(@.type=="Approved")].status}' | grep -q True; }
crt_is_jane() { openssl x509 -in "$CQ_WORK/61/jane.crt" -noout -subject 2>/dev/null | grep -q "CN *= *jane"; }
crt_matches_key() { [ "$(openssl x509 -in "$CQ_WORK/61/jane.crt" -noout -pubkey 2>/dev/null)" = "$(openssl pkey -in "$CQ_WORK/61/jane.key" -pubout 2>/dev/null)" ]; }
check "CSR jane uses signer kube-apiserver-client" field_eq - csr/jane '{.spec.signerName}' kubernetes.io/kube-apiserver-client
check 2 "CSR jane is approved and issued" approved
check 2 "jane.crt is a PEM cert for CN=jane" crt_is_jane
check "jane.crt belongs to jane.key" crt_matches_key
check 2 "jane can list pods in dev-team" can_i jane list pods dev-team
check "jane cannot delete pods in dev-team" cannot_i jane delete pods dev-team
check "jane cannot list pods in default" cannot_i jane list pods default""",
    solve="""W="$CQ_WORK/61"
cat <<EOF | kubectl apply -f -
apiVersion: certificates.k8s.io/v1
kind: CertificateSigningRequest
metadata:
  name: jane
spec:
  request: $(base64 -w0 < "$W/jane.csr")
  signerName: kubernetes.io/kube-apiserver-client
  usages: [client auth]
EOF
kubectl certificate approve jane
cq_wait 30 bash -c '[ -n "$(kubectl get csr jane -o jsonpath={.status.certificate})" ]'
kubectl get csr jane -o jsonpath='{.status.certificate}' | base64 -d > "$W/jane.crt"
kubectl create role pod-reader -n dev-team --verb=get,list,watch --resource=pods
kubectl create rolebinding jane-pod-reader -n dev-team --role=pod-reader --user=jane""",
    cleanup="kubectl delete csr jane --ignore-not-found >/dev/null 2>&1",
    hints=["Write the CSR object yourself. The docs page has a full example under 'Create a CertificateSigningRequest'. The request field is the CSR file in base64 on one line: `base64 -w0 jane.csr`.",
           "`k get csr` shows Pending. `k certificate approve jane`. The cert is in `.status.certificate`, base64 encoded.",
           "`k get csr jane -o jsonpath='{.status.certificate}' | base64 -d > jane.crt`. Then `k create role` and `k create rolebinding --user=jane`."],
    solution="""```bash
cd ~/ckaquest-work/61
cat <<EOF > csr.yaml
apiVersion: certificates.k8s.io/v1
kind: CertificateSigningRequest
metadata:
  name: jane
spec:
  request: $(base64 -w0 < jane.csr)
  signerName: kubernetes.io/kube-apiserver-client
  usages: [client auth]
EOF
k apply -f csr.yaml
k certificate approve jane
k get csr jane -o jsonpath='{.status.certificate}' | base64 -d > jane.crt
k create role pod-reader -n dev-team --verb=get,list,watch --resource=pods
k create rolebinding jane-pod-reader -n dev-team --role=pod-reader --user=jane
k auth can-i list pods -n dev-team --as=jane    # yes
```""",
    debrief="""# A New User Called Jane

## What happened
Kubernetes has no user objects. A user is whoever presents a client certificate signed by the cluster CA. The CN becomes the user name and each O becomes a group.

The CSR API lets an admin sign such a certificate without touching the CA key files.

## Steps to know by heart
1. `openssl genrsa` and `openssl req -subj "/CN=jane/O=dev"` (often already done for you in the exam).
2. CSR object with `signerName: kubernetes.io/kube-apiserver-client` and `usages: [client auth]`.
3. `k certificate approve jane`.
4. Pull the cert from `.status.certificate` and base64-decode it.
5. RBAC for the user. Without it, jane can log in but do nothing.

## Exam angle
- The CSR is often given as a file. `base64 -w0` keeps it on one line. Without `-w0` the YAML breaks.
- Check your work with `k auth can-i ... --as=jane`. You do not need a kubeconfig for jane to prove RBAC.
- `k certificate deny` exists too.

Bookmark: https://kubernetes.io/docs/reference/access-authn-authz/certificate-signing-requests/#normal-user

Your notes: Certificates API, RBAC, TLS in Kubernetes""")

level(W, "level-62-clusterrole", dict(
    name="Nodes Are Cluster-Wide",
    description="A monitoring agent must read nodes but a Role cannot grant that",
    objective="Grant cluster-wide read access to nodes with a ClusterRole",
    xp=250, difficulty="intermediate", expected_time="6m", domain="architecture", course_section=7,
    namespace="monitoring", concepts=["ClusterRole", "ClusterRoleBinding", "cluster-scoped resources"],
    task="""ServiceAccount **node-inspector** in namespace **monitoring** must be able to `get`, `list` and `watch` nodes.

Create a ClusterRole **node-reader** and a ClusterRoleBinding **node-inspector-binding** for it. Grant nothing else.""",
    docs=["https://kubernetes.io/docs/reference/access-authn-authz/rbac/#clusterrole-example"]),
    setup="kubectl create serviceaccount node-inspector -n monitoring >/dev/null\nkubectl delete clusterrole node-reader --ignore-not-found >/dev/null\nkubectl delete clusterrolebinding node-inspector-binding --ignore-not-found >/dev/null",
    validate="""SA=system:serviceaccount:monitoring:node-inspector
check "ClusterRole node-reader exists" exists - clusterrole/node-reader
check "ClusterRoleBinding node-inspector-binding uses node-reader" field_eq - clusterrolebinding/node-inspector-binding '{.roleRef.name}' node-reader
check 2 "node-inspector can list nodes" can_i "$SA" list nodes
check "node-inspector can watch nodes" can_i "$SA" watch nodes
check "node-inspector cannot delete nodes" cannot_i "$SA" delete nodes
check "node-inspector cannot list secrets anywhere" cannot_i "$SA" list secrets kube-system""",
    solve="""kubectl create clusterrole node-reader --verb=get,list,watch --resource=nodes
kubectl create clusterrolebinding node-inspector-binding --clusterrole=node-reader --serviceaccount=monitoring:node-inspector""",
    cleanup="kubectl delete clusterrolebinding node-inspector-binding --ignore-not-found >/dev/null 2>&1\nkubectl delete clusterrole node-reader --ignore-not-found >/dev/null 2>&1",
    hints=["Nodes have no namespace. Check with `k api-resources --namespaced=false | grep nodes`.",
           "A Role lives in a namespace and can only grant namespaced resources. You need the cluster-wide versions.",
           "`k create clusterrole node-reader --verb=get,list,watch --resource=nodes` and `k create clusterrolebinding ... --serviceaccount=monitoring:node-inspector`."],
    solution="""```bash
k create clusterrole node-reader --verb=get,list,watch --resource=nodes
k create clusterrolebinding node-inspector-binding --clusterrole=node-reader --serviceaccount=monitoring:node-inspector
k auth can-i list nodes --as=system:serviceaccount:monitoring:node-inspector
```""",
    debrief="""# Nodes Are Cluster-Wide

## What happened
Nodes, PersistentVolumes, StorageClasses, ClusterRoles and namespaces themselves are cluster-scoped. Only a ClusterRole can grant access to them, and only a ClusterRoleBinding makes that grant cluster-wide.

## The four combinations
- Role + RoleBinding: namespaced resources, one namespace.
- ClusterRole + RoleBinding: reuse one ClusterRole, but only inside the RoleBinding's namespace.
- ClusterRole + ClusterRoleBinding: everywhere, including cluster-scoped resources.
- Role + ClusterRoleBinding: not possible.

## Exam angle
- `--serviceaccount=<ns>:<name>` is the format. A missing namespace is a common mistake.
- `k api-resources --namespaced=false` lists what needs a ClusterRole.
- Test as the SA: `--as=system:serviceaccount:<ns>:<name>`.

Bookmark: https://kubernetes.io/docs/reference/access-authn-authz/rbac/

Your notes: Cluster Roles, RBAC, Service Accounts""")

level(W, "level-63-sa-forbidden", dict(
    name="403 From Inside the Pod",
    description="A report job logs Forbidden when it reads ConfigMaps",
    objective="Find the ServiceAccount the job uses and give it exactly the access it needs",
    xp=250, difficulty="intermediate", expected_time="8m", domain="architecture", course_section=7,
    namespace="reports", concepts=["ServiceAccount", "Forbidden", "Role", "kubectl logs"],
    task="""Deployment **report-gen** in namespace **reports** logs `Forbidden` errors.

Find out which ServiceAccount it runs as and what it tries to do. Give that ServiceAccount exactly that access in namespace **reports** with a Role **cm-reader** and a RoleBinding **cm-reader-binding**. Do not change the Deployment.""",
    docs=["https://kubernetes.io/docs/reference/access-authn-authz/rbac/",
          "https://kubernetes.io/docs/tasks/configure-pod-container/configure-service-account/"]),
    setup="""kubectl create serviceaccount report-sa -n reports >/dev/null
kubectl create configmap report-settings -n reports --from-literal=format=pdf >/dev/null
cat <<'EOF' | kubectl apply -f - >/dev/null
apiVersion: apps/v1
kind: Deployment
metadata:
  name: report-gen
  namespace: reports
spec:
  replicas: 1
  selector:
    matchLabels: {app: report-gen}
  template:
    metadata:
      labels: {app: report-gen}
    spec:
      serviceAccountName: report-sa
      containers:
      - name: gen
        image: bitnami/kubectl:latest
        command: ["sh", "-c", "while true; do kubectl get configmaps -n reports -o name 2>&1 | tail -2; sleep 5; done"]
EOF""",
    validate="""SA=system:serviceaccount:reports:report-sa
works() { kubectl logs deploy/report-gen -n reports --tail=2 2>/dev/null | grep -q "configmap/report-settings"; }
check "Deployment still runs as report-sa" field_eq reports deploy/report-gen '{.spec.template.spec.serviceAccountName}' report-sa
check 2 "report-sa can list configmaps in reports" can_i "$SA" list configmaps reports
check "report-sa cannot read secrets" cannot_i "$SA" get secrets reports
check "report-sa cannot change configmaps" cannot_i "$SA" delete configmaps reports
check 2 "the job now lists configmaps" works""",
    solve="""kubectl create role cm-reader -n reports --verb=get,list --resource=configmaps
kubectl create rolebinding cm-reader-binding -n reports --role=cm-reader --serviceaccount=reports:report-sa
sleep 12""",
    hints=["`k logs deploy/report-gen -n reports`. The error names the user and the verb.",
           "The user is `system:serviceaccount:reports:report-sa`. It wants to list configmaps.",
           "`k create role cm-reader --verb=get,list --resource=configmaps -n reports`, then a rolebinding with `--serviceaccount=reports:report-sa`."],
    solution="""```bash
k logs deploy/report-gen -n reports
# User "system:serviceaccount:reports:report-sa" cannot list resource "configmaps"
k create role cm-reader -n reports --verb=get,list --resource=configmaps
k create rolebinding cm-reader-binding -n reports --role=cm-reader --serviceaccount=reports:report-sa
k logs deploy/report-gen -n reports -f
```""",
    debrief="""# 403 From Inside the Pod

## What happened
Every pod runs as a ServiceAccount (`default` if none is set). Its token is mounted at `/var/run/secrets/kubernetes.io/serviceaccount/`. RBAC decides what that identity may do. A new ServiceAccount may do nothing.

## Read the error
`User "system:serviceaccount:reports:report-sa" cannot list resource "configmaps" in API group "" in the namespace "reports"` tells you the who, the verb, the resource, the API group and the namespace. That is all you need for the Role.

## Exam angle
- Grant the least: the verbs and resources from the error, no more.
- `k get deploy report-gen -o jsonpath='{.spec.template.spec.serviceAccountName}'` finds the SA.
- `automountServiceAccountToken: false` stops the token mount when a pod does not need the API.

Bookmark: https://kubernetes.io/docs/reference/access-authn-authz/rbac/

Your notes: Service Accounts, RBAC""")

level(W, "level-64-cert-renew", dict(
    name="Certificate Renewal",
    description="The API server certificate must be renewed",
    objective="Record the old expiry date, renew the apiserver certificate and make the API server use it",
    xp=350, difficulty="advanced", expected_time="12m", domain="architecture", course_section=7,
    namespace="cert-lab", concepts=["kubeadm certs", "openssl x509", "static pod restart"],
    task="""On node **controlplane**:

1. Write the current expiry date of the kube-apiserver serving certificate to `/opt/course/64/expiry-before.txt`. Use the exact output of `openssl x509 -noout -enddate` (one line, starts with `notAfter=`).
2. Renew only the **apiserver** certificate with kubeadm.
3. Make sure the running API server serves the new certificate.""",
    docs=["https://kubernetes.io/docs/tasks/administer-cluster/kubeadm/kubeadm-certs/"]),
    setup="""cq_node_sh controlplane 'mkdir -p /opt/course/64 /root/.cq-backup
mv -f /opt/course/64/expiry-before.txt /root/.cq-backup/64-old-answer 2>/dev/null || true
openssl x509 -in /etc/kubernetes/pki/apiserver.crt -noout -enddate > /root/.cq-backup/64-enddate'""",
    validate="""orig() { cq_node_sh controlplane 'cat /root/.cq-backup/64-enddate'; }
answer_ok() { [ "$(cq_node_sh controlplane 'cat /opt/course/64/expiry-before.txt' 2>/dev/null | tr -d '[:space:]')" = "$(orig | tr -d '[:space:]')" ]; }
renewed() { [ "$(cq_node_sh controlplane 'openssl x509 -in /etc/kubernetes/pki/apiserver.crt -noout -enddate')" != "$(orig)" ]; }
served() { cq_node_sh controlplane '[ "$(openssl x509 -in /etc/kubernetes/pki/apiserver.crt -noout -serial)" = "$(echo | openssl s_client -connect 127.0.0.1:6443 2>/dev/null | openssl x509 -noout -serial)" ]'; }
check 2 "expiry-before.txt has the old notAfter line" answer_ok
check 2 "apiserver.crt was renewed" renewed
check 2 "the API server serves the renewed certificate" served
check "API server answers" cq_api_up""",
    solve="""cq_node_sh controlplane 'openssl x509 -in /etc/kubernetes/pki/apiserver.crt -noout -enddate > /opt/course/64/expiry-before.txt
sleep 1
kubeadm certs renew apiserver
mv /etc/kubernetes/manifests/kube-apiserver.yaml /root/
sleep 20
mv /root/kube-apiserver.yaml /etc/kubernetes/manifests/'
cq_wait_api 180""",
    cleanup="cq_wait_api 180 || true",
    hints=["`openssl x509 -in /etc/kubernetes/pki/apiserver.crt -noout -enddate > /opt/course/64/expiry-before.txt` before you renew.",
           "`kubeadm certs check-expiration` lists every cert. `kubeadm certs renew apiserver` renews one.",
           "kubeadm writes the new file, but the running API server still has the old cert in memory. Restart the static pod: move its manifest out of /etc/kubernetes/manifests, wait until the container is gone (`crictl ps`), move it back."],
    solution="""```bash
ssh controlplane
openssl x509 -in /etc/kubernetes/pki/apiserver.crt -noout -enddate > /opt/course/64/expiry-before.txt
kubeadm certs check-expiration
kubeadm certs renew apiserver
mv /etc/kubernetes/manifests/kube-apiserver.yaml /root/
watch crictl ps          # wait until kube-apiserver is gone
mv /root/kube-apiserver.yaml /etc/kubernetes/manifests/
kubeadm certs check-expiration | grep apiserver
```""",
    debrief="""# Certificate Renewal

## What happened
kubeadm certificates last one year. `kubeadm upgrade` renews them, so clusters that are upgraded often never expire. Otherwise you renew by hand.

`kubeadm certs renew` only writes new files. Static pods read their certs at start, so you must restart them.

## Restarting a static pod
There is no `kubectl rollout restart` for static pods. Deleting the mirror pod does nothing. Move the manifest out of the manifests folder, wait for the kubelet to stop the container, move it back.

## Exam angle
- `kubeadm certs check-expiration` is the fastest overview.
- `openssl x509 -in <crt> -noout -text` shows issuer, SANs and dates. `-enddate` only the expiry.
- Cert files live in `/etc/kubernetes/pki/`. The etcd ones in `/etc/kubernetes/pki/etcd/`.

Bookmark: https://kubernetes.io/docs/tasks/administer-cluster/kubeadm/kubeadm-certs/

Your notes: TLS in Kubernetes, Cluster Upgrade""")

level(W, "level-65-etcd-backup", dict(
    name="Back Up etcd",
    description="Take an etcd snapshot before a risky change",
    objective="Save an etcd snapshot on the control plane",
    xp=300, difficulty="intermediate", expected_time="8m", domain="architecture", course_section=6,
    namespace="backup-lab", concepts=["etcdctl snapshot save", "etcd certificates", "etcdutl snapshot status"],
    task="""On node **controlplane**, save a snapshot of etcd to `/opt/course/65/etcd-snapshot.db`.

Find the endpoint and the certificate files yourself. Then write the output of `etcdutl snapshot status /opt/course/65/etcd-snapshot.db -w table` to `/opt/course/65/status.txt`.""",
    docs=["https://kubernetes.io/docs/tasks/administer-cluster/configure-upgrade-etcd/#backing-up-an-etcd-cluster"]),
    setup="""cq_node_sh controlplane 'mkdir -p /opt/course/65 /root/.cq-trash; mv -f /opt/course/65/* /root/.cq-trash/ 2>/dev/null || true'""",
    validate="""check 2 "etcd-snapshot.db exists" node_ok controlplane 'test -s /opt/course/65/etcd-snapshot.db'
check 2 "the snapshot is valid" node_ok controlplane 'etcdutl snapshot status /opt/course/65/etcd-snapshot.db'
check "status.txt has the status table" node_ok controlplane 'grep -q HASH /opt/course/65/status.txt'""",
    solve="""cq_node_sh controlplane 'ETCDCTL_API=3 etcdctl --endpoints=https://127.0.0.1:2379 \\
  --cacert=/etc/kubernetes/pki/etcd/ca.crt --cert=/etc/kubernetes/pki/etcd/server.crt --key=/etc/kubernetes/pki/etcd/server.key \\
  snapshot save /opt/course/65/etcd-snapshot.db
etcdutl snapshot status /opt/course/65/etcd-snapshot.db -w table > /opt/course/65/status.txt'""",
    cleanup="cq_node_sh controlplane 'mkdir -p /root/.cq-trash; mv -f /opt/course/65/* /root/.cq-trash/ 2>/dev/null || true'",
    hints=["The etcd static pod manifest has everything: `grep -E 'listen-client|cert|key|trusted' /etc/kubernetes/manifests/etcd.yaml`.",
           "You need `--endpoints`, `--cacert`, `--cert` and `--key`. The CA is etcd's own CA, not the cluster CA.",
           "`etcdctl --endpoints=https://127.0.0.1:2379 --cacert=/etc/kubernetes/pki/etcd/ca.crt --cert=/etc/kubernetes/pki/etcd/server.crt --key=/etc/kubernetes/pki/etcd/server.key snapshot save /opt/course/65/etcd-snapshot.db`"],
    solution="""```bash
ssh controlplane
grep -E 'listen-client|cert-file|key-file|trusted-ca' /etc/kubernetes/manifests/etcd.yaml
etcdctl --endpoints=https://127.0.0.1:2379 \\
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \\
  --cert=/etc/kubernetes/pki/etcd/server.crt \\
  --key=/etc/kubernetes/pki/etcd/server.key \\
  snapshot save /opt/course/65/etcd-snapshot.db
etcdutl snapshot status /opt/course/65/etcd-snapshot.db -w table > /opt/course/65/status.txt
```""",
    debrief="""# Back Up etcd

## What happened
etcd holds the whole cluster state. A snapshot is a single file you can restore later.

## Where the flags come from
The etcd manifest at `/etc/kubernetes/manifests/etcd.yaml`:
- `--listen-client-urls` gives the endpoint.
- `--trusted-ca-file` gives `--cacert`.
- `--cert-file` and `--key-file` give `--cert` and `--key`. The `healthcheck-client` or `apiserver-etcd-client` pairs work too.

## etcdctl or etcdutl
Since etcd 3.5, `etcdutl` does the offline work: `snapshot status` and `snapshot restore`. `etcdctl` talks to a running etcd and does `snapshot save`. Old commands like `etcdctl snapshot restore` still print a deprecation warning. Both work in the exam.

## Exam angle
- Copy the cert paths from the manifest. Do not type them from memory.
- `ETCDCTL_API=3` is the default now. Setting it does no harm.
- Write to exactly the path the task names.

Bookmark: https://kubernetes.io/docs/tasks/administer-cluster/configure-upgrade-etcd/

Your notes: Backup and Restore""")

level(W, "level-66-etcd-restore", dict(
    name="Restore etcd",
    description="Someone deleted the ledger. A snapshot from before exists.",
    objective="Restore etcd from the snapshot so the deleted data comes back",
    xp=450, difficulty="expert", expected_time="15m", domain="architecture", course_section=6,
    namespace="payments", concepts=["etcdutl snapshot restore", "etcd data dir", "static pod hostPath"],
    task="""ConfigMap **ledger** in namespace **payments** was deleted by mistake. A snapshot taken before that is at `/opt/course/66/etcd-backup.db` on node **controlplane**.

Restore the snapshot into the data directory `/var/lib/etcd-restore` and make etcd run from it. ConfigMap **ledger** must exist again and the API server must work.""",
    docs=["https://kubernetes.io/docs/tasks/administer-cluster/configure-upgrade-etcd/#restoring-an-etcd-cluster"]),
    setup="""kubectl create configmap ledger -n payments --from-literal=balance=1000000 >/dev/null
cq_node_backup controlplane /etc/kubernetes/manifests/etcd.yaml
cq_node_sh controlplane 'mkdir -p /opt/course/66 /root/.cq-trash
[ -d /var/lib/etcd-restore ] && mv /var/lib/etcd-restore /root/.cq-trash/etcd-restore-$(date +%s)
mv -f /opt/course/66/etcd-backup.db /root/.cq-trash/ 2>/dev/null || true
etcdctl --endpoints=https://127.0.0.1:2379 --cacert=/etc/kubernetes/pki/etcd/ca.crt \\
  --cert=/etc/kubernetes/pki/etcd/server.crt --key=/etc/kubernetes/pki/etcd/server.key \\
  snapshot save /opt/course/66/etcd-backup.db >/dev/null 2>&1'
kubectl delete configmap ledger -n payments >/dev/null""",
    validate="""check 2 "etcd runs from /var/lib/etcd-restore" node_ok controlplane 'grep -q "path: /var/lib/etcd-restore" /etc/kubernetes/manifests/etcd.yaml'
check "API server answers" cq_api_up
check 3 "ConfigMap ledger is back" field_eq payments cm/ledger '{.data.balance}' 1000000
check "all nodes Ready" all_nodes_ready""",
    solve="""cq_node_sh controlplane 'etcdutl snapshot restore /opt/course/66/etcd-backup.db --data-dir /var/lib/etcd-restore
sed -i "s|path: /var/lib/etcd$|path: /var/lib/etcd-restore|" /etc/kubernetes/manifests/etcd.yaml'
sleep 20
cq_wait_api 240""",
    cleanup="""source "$CQ_ROOT/lib/common.sh"
cq_restore_manifest etcd
sleep 15
cq_wait_api 300 || true
kubectl delete configmap ledger -n payments --ignore-not-found >/dev/null 2>&1 || true""",
    hints=["`etcdutl snapshot restore <file> --data-dir <new dir>` writes a fresh data directory. No certs needed, it works on files.",
           "etcd still reads its old data. Look at the `volumes:` section of /etc/kubernetes/manifests/etcd.yaml. Which hostPath is mounted as the data dir?",
           "Change the `etcd-data` hostPath to /var/lib/etcd-restore. The kubelet restarts etcd. The API server needs a minute to come back. `watch crictl ps`."],
    solution="""```bash
ssh controlplane
etcdutl snapshot restore /opt/course/66/etcd-backup.db --data-dir /var/lib/etcd-restore
vim /etc/kubernetes/manifests/etcd.yaml
#   volumes:
#   - hostPath:
#       path: /var/lib/etcd-restore     # was /var/lib/etcd
#     name: etcd-data
watch crictl ps                         # etcd and kube-apiserver restart
exit
k get cm ledger -n payments
```""",
    debrief="""# Restore etcd

## What happened
A restore never writes into the running data directory. It creates a new one from the snapshot. Then you point etcd at it.

## Two ways to point etcd at the new dir
1. Change the `hostPath` of the `etcd-data` volume (done here). The path inside the container stays `/var/lib/etcd`, so `--data-dir` does not change.
2. Change both `--data-dir` and the volume mount. More edits, more chances for a typo.

## Things that go wrong
- Restoring into an existing directory fails. Pick a new path.
- The API server is down for a minute while etcd restarts. Wait with `crictl ps`, do not edit more.
- Everything created after the snapshot is gone. That is the point of a restore.

## Exam angle
- `etcdutl snapshot restore` needs no endpoint or certs.
- Note the old path before you edit, so you can undo.
- Check with `k get` on the object the task names.

Bookmark: https://kubernetes.io/docs/tasks/administer-cluster/configure-upgrade-etcd/#restoring-an-etcd-cluster

Your notes: Backup and Restore, Control Plane""")

level(W, "level-67-kubeconfig-repair", dict(
    name="Broken kubeconfig",
    description="kubectl on the control plane cannot talk to the cluster",
    objective="Repair /root/.kube/config on the control plane",
    xp=250, difficulty="intermediate", expected_time="8m", domain="troubleshooting", course_section=7,
    namespace="kubeconfig-lab", concepts=["kubeconfig", "contexts", "kubectl config"],
    task="""On node **controlplane**, `kubectl get nodes` fails. The kubeconfig at `/root/.kube/config` was edited by hand.

Repair that file so `kubectl get nodes` works on controlplane again. Do not replace it with a different file and do not set `KUBECONFIG`.""",
    docs=["https://kubernetes.io/docs/concepts/configuration/organize-cluster-access-kubeconfig/",
          "https://kubernetes.io/docs/reference/kubectl/generated/kubectl_config/"]),
    setup="""cq_node_backup controlplane /root/.kube/config
cq_node_sh controlplane "sed -i -e 's|:6443|:6444|' -e 's|^current-context: .*|current-context: kubernetes-admin@kubernetez|' /root/.kube/config\"""",
    validate="""check 2 "the server points at port 6443" node_ok controlplane 'grep -q "server: https://.*:6443" /root/.kube/config'
check 2 "current-context exists in the file" node_ok controlplane 'kubectl config get-contexts "$(kubectl config current-context)"'
check 2 "kubectl get nodes works on controlplane" node_ok controlplane 'kubectl get nodes'""",
    solve="""cq_node_sh controlplane "sed -i -e 's|:6444|:6443|' -e 's|^current-context: .*|current-context: kubernetes-admin@ckaquest|' /root/.kube/config"
cq_node_sh controlplane 'kubectl config get-contexts -o name | head -1 | xargs kubectl config use-context'""",
    cleanup="cq_node_restore controlplane /root/.kube/config",
    hints=["Read the error carefully. `kubectl config view` and `kubectl config get-contexts` work even when the server is unreachable.",
           "There are two faults. One is about which context is active, one is about where the server is.",
           "`kubectl config use-context <real name>`, and fix the port in the `server:` line. The API server listens on 6443 (`ss -lntp | grep apiserver`)."],
    solution="""```bash
ssh controlplane
kubectl get nodes                   # error: context "kubernetes-admin@kubernetez" does not exist
kubectl config get-contexts
kubectl config use-context kubernetes-admin@ckaquest
kubectl get nodes                   # connection refused on :6444
ss -lntp | grep apiserver           # 6443
vim /root/.kube/config              # server: https://...:6443
kubectl get nodes
```""",
    debrief="""# Broken kubeconfig

## What happened
A kubeconfig has three lists (clusters, users, contexts) and one `current-context`. A context joins one cluster, one user and an optional namespace.

Two faults: `current-context` named a context that does not exist, and the cluster server had the wrong port.

## Read-only commands that always work
- `kubectl config view` (add `--raw` to see cert data)
- `kubectl config get-contexts`
- `kubectl config current-context`

## Exam angle
- Every exam task starts with a `kubectl config use-context` line. Run it every time.
- Fixes: `kubectl config set-cluster <name> --server=...`, `kubectl config use-context`, `kubectl config set-context --current --namespace=...`.
- The admin kubeconfig on a kubeadm control plane is `/etc/kubernetes/admin.conf`. Compare with it.

Bookmark: https://kubernetes.io/docs/concepts/configuration/organize-cluster-access-kubeconfig/

Your notes: KubeConfig""")

level(W, "level-68-static-pod", dict(
    name="A Pod Without the API",
    description="Run a pod on node01 that the kubelet manages by itself",
    objective="Create a static pod on node01",
    xp=250, difficulty="intermediate", expected_time="6m", domain="architecture", course_section=3,
    namespace="static-lab", concepts=["static pods", "staticPodPath", "mirror pods"],
    task="""Create a static pod **static-web** on node **node01** in namespace **static-lab**. Image `nginx:1.27-alpine`, container port 80, label `app=static-web`.

The pod must show up in `kubectl get pods -n static-lab`.""",
    docs=["https://kubernetes.io/docs/tasks/configure-pod-container/static-pod/"]),
    setup="""cq_node_sh node01 'mkdir -p /root/.cq-trash; [ -f /etc/kubernetes/manifests/static-web.yaml ] && mv /etc/kubernetes/manifests/static-web.yaml /root/.cq-trash/ || true'""",
    validate="""N="static-web-$(cq_node_name node01)"
check "a manifest for static-web is in node01's staticPodPath" node_ok node01 'grep -rl "name: static-web" "$(awk "/staticPodPath/ {print \\$2}" /var/lib/kubelet/config.yaml)"'
check 2 "mirror pod $N is Ready" pod_ready static-lab "$N"
check "it runs nginx:1.27-alpine" field_eq static-lab "pod/$N" '{.spec.containers[0].image}' nginx:1.27-alpine
check "it has label app=static-web" field_eq static-lab "pod/$N" '{.metadata.labels.app}' static-web""",
    solve="""kubectl run static-web -n static-lab --image=nginx:1.27-alpine --port=80 --labels=app=static-web --dry-run=client -o yaml > /tmp/cq-static-web.yaml
cq_node_put node01 /tmp/cq-static-web.yaml /etc/kubernetes/manifests/static-web.yaml
cq_wait 90 kubectl get pod "static-web-$(cq_node_name node01)" -n static-lab""",
    cleanup="""cq_node_sh node01 'mkdir -p /root/.cq-trash; [ -f /etc/kubernetes/manifests/static-web.yaml ] && mv /etc/kubernetes/manifests/static-web.yaml /root/.cq-trash/static-web.$(date +%s).yaml || true'""",
    hints=["Generate the YAML on your terminal: `k run static-web -n static-lab --image=nginx:1.27-alpine --port=80 -l app=static-web $do`.",
           "The kubelet on node01 watches a folder. Find it: `ssh node01`, then `grep staticPodPath /var/lib/kubelet/config.yaml`.",
           "Put the YAML file in that folder on node01. The mirror pod is called static-web-<node name>."],
    solution="""```bash
k run static-web -n static-lab --image=nginx:1.27-alpine --port=80 -l app=static-web $do > static-web.yaml
ssh node01
grep staticPodPath /var/lib/kubelet/config.yaml      # /etc/kubernetes/manifests
vim /etc/kubernetes/manifests/static-web.yaml        # paste the YAML
exit
k get pods -n static-lab -o wide
```""",
    debrief="""# A Pod Without the API

## What happened
The kubelet runs every manifest in its `staticPodPath`, without the scheduler or the API server. It then creates a read-only mirror pod in the API so you can see it. The name gets `-<node name>` appended.

## Facts to remember
- Delete the file to delete the pod. `k delete pod` only removes the mirror, which comes back.
- Static pods cannot use ServiceAccounts, ConfigMaps or Secrets from the API.
- The control plane of a kubeadm cluster is static pods: etcd, apiserver, controller-manager, scheduler.

## Exam angle
- Generate YAML with `k run ... $do` on your terminal, then paste it on the node.
- Always check `staticPodPath` in `/var/lib/kubelet/config.yaml`. A task may have changed it.
- `ps aux | grep kubelet` shows which config file the kubelet uses.

Bookmark: https://kubernetes.io/docs/tasks/configure-pod-container/static-pod/

Your notes: Static Pods""")

level(W, "level-69-admission-plugin", dict(
    name="Admission Control",
    description="The team wants namespaces to be created automatically",
    objective="Enable an admission plugin on the API server",
    xp=300, difficulty="advanced", expected_time="10m", domain="architecture", course_section=3,
    namespace="admission-lab", concepts=["admission controllers", "kube-apiserver flags", "--enable-admission-plugins"],
    task="""Enable the admission plugin **NamespaceAutoProvision** on the kube-apiserver. Keep the plugins that are already enabled.

Then create pod **probe** (image `busybox:1.36`, command `sleep 3600`) in namespace **auto-created**, without creating the namespace first.""",
    docs=["https://kubernetes.io/docs/reference/access-authn-authz/admission-controllers/",
          "https://kubernetes.io/docs/reference/command-line-tools-reference/kube-apiserver/"]),
    setup="""cq_node_backup controlplane /etc/kubernetes/manifests/kube-apiserver.yaml
kubectl delete namespace auto-created --ignore-not-found --timeout=90s >/dev/null""",
    validate="""check 2 "NamespaceAutoProvision is enabled" node_ok controlplane 'grep -- "--enable-admission-plugins=" /etc/kubernetes/manifests/kube-apiserver.yaml | grep -q NamespaceAutoProvision'
check "NodeRestriction is still enabled" node_ok controlplane 'grep -- "--enable-admission-plugins=" /etc/kubernetes/manifests/kube-apiserver.yaml | grep -q NodeRestriction'
check "API server answers" cq_api_up
check 2 "pod probe exists in auto-created" exists auto-created pod/probe""",
    solve="""cq_node_sh controlplane "sed -i 's|--enable-admission-plugins=NodeRestriction|--enable-admission-plugins=NodeRestriction,NamespaceAutoProvision|' /etc/kubernetes/manifests/kube-apiserver.yaml"
sleep 25
cq_wait_api 240
cq_wait 60 kubectl run probe -n auto-created --image=busybox:1.36 -- sleep 3600""",
    cleanup="""cq_restore_manifest kube-apiserver
sleep 15
cq_wait_api 240 || true
kubectl delete namespace auto-created --ignore-not-found --wait=false >/dev/null 2>&1 || true""",
    hints=["The plugins are a flag in /etc/kubernetes/manifests/kube-apiserver.yaml on controlplane.",
           "Add to the existing list with a comma: `--enable-admission-plugins=NodeRestriction,NamespaceAutoProvision`.",
           "Saving the manifest restarts the API server. Wait until `kubectl get nodes` works, then `k run probe -n auto-created --image=busybox:1.36 -- sleep 3600`."],
    solution="""```bash
ssh controlplane
vim /etc/kubernetes/manifests/kube-apiserver.yaml
#   - --enable-admission-plugins=NodeRestriction,NamespaceAutoProvision
watch crictl ps            # wait for kube-apiserver
exit
k run probe -n auto-created --image=busybox:1.36 -- sleep 3600
k get ns auto-created
```""",
    debrief="""# Admission Control

## What happened
After authentication and authorization, every write request passes admission plugins. They can reject it (validating) or change it (mutating). NamespaceAutoProvision creates a missing namespace on the fly.

## Facts to remember
- Many plugins are on by default. `kube-apiserver -h | grep enable-admission-plugins` lists them. Run it inside the apiserver container with crictl exec, or read the docs.
- `--enable-admission-plugins` adds to the defaults. `--disable-admission-plugins` removes defaults.
- NamespaceExists and NamespaceLifecycle are related. NamespaceAutoProvision is off by default.

## Exam angle
- Edit the flag, keep the existing values, use commas, no spaces.
- A typo in a plugin name stops the API server. Check `crictl logs` if it does not come back.

Bookmark: https://kubernetes.io/docs/reference/access-authn-authz/admission-controllers/

Your notes: Admission Controllers""")

level(W, "level-70-join-token", dict(
    name="A Ticket to Join",
    description="A new worker needs a join command",
    objective="Create a bootstrap token with a short TTL and save the join command",
    xp=200, difficulty="intermediate", expected_time="5m", domain="architecture", course_section=11,
    namespace="join-lab", concepts=["kubeadm token", "bootstrap tokens", "kubeadm join"],
    task="""On node **controlplane**, create a new bootstrap token that expires after **2 hours** and print the full join command.

Save the join command to `/opt/course/70/join.sh`.""",
    docs=["https://kubernetes.io/docs/reference/setup-tools/kubeadm/kubeadm-token/"]),
    setup="""cq_node_sh controlplane 'mkdir -p /opt/course/70 /root/.cq-trash; mv -f /opt/course/70/join.sh /root/.cq-trash/ 2>/dev/null || true'""",
    validate="""token() { cq_node_sh controlplane "grep -o -- '--token [a-z0-9.]*' /opt/course/70/join.sh | cut -d' ' -f2"; }
listed() { local t; t="$(token)"; [ -n "$t" ] && cq_node_sh controlplane "kubeadm token list | grep -q '^$t'"; }
ttl_ok() { local t; t="$(token)"; cq_node_sh controlplane "kubeadm token list | grep '^$t' | awk '{print \\$2}'" | grep -Eq '^(1h[0-9]+m|2h|1h)'; }
check "join.sh has a kubeadm join command" node_ok controlplane 'grep -q "kubeadm join .*--discovery-token-ca-cert-hash sha256:" /opt/course/70/join.sh'
check 2 "the token in join.sh exists" listed
check 2 "the token expires in about 2 hours" ttl_ok""",
    solve="""cq_node_sh controlplane 'kubeadm token create --ttl 2h --print-join-command > /opt/course/70/join.sh'""",
    cleanup="""t="$(cq_node_sh controlplane "grep -o -- '--token [a-z0-9.]*' /opt/course/70/join.sh 2>/dev/null | cut -d' ' -f2")"
[ -n "$t" ] && cq_node_sh controlplane "kubeadm token delete $t" >/dev/null 2>&1
true""",
    hints=["`kubeadm token -h`. You want create.", "`--ttl` sets the lifetime. Another flag prints the whole join command for you.", "`kubeadm token create --ttl 2h --print-join-command > /opt/course/70/join.sh`"],
    solution="""```bash
ssh controlplane
kubeadm token create --ttl 2h --print-join-command > /opt/course/70/join.sh
kubeadm token list
```""",
    debrief="""# A Ticket to Join

## What happened
`kubeadm join` needs a bootstrap token (who may join) and the CA cert hash (proof the worker talks to the right cluster). The token from `kubeadm init` expires after 24 hours.

## Commands
- `kubeadm token create --print-join-command` makes a new token and prints the whole command.
- `kubeadm token list`, `kubeadm token delete <token>`.
- The hash by hand: `openssl x509 -pubkey -in /etc/kubernetes/pki/ca.crt | openssl rsa -pubin -outform der 2>/dev/null | openssl dgst -sha256 -hex`.

## Exam angle
- Adding a node is part of the curriculum. Run the printed command on the new node as root.
- `--ttl 0` means the token never expires. Avoid it.

Bookmark: https://kubernetes.io/docs/reference/setup-tools/kubeadm/kubeadm-token/

Your notes: Cluster Upgrade, Control Plane""")
