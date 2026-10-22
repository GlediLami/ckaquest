"""Writes World 15 (the last curriculum gaps: kubectl debug, choosing policies, aggregation,
EndpointSlices, multi-metric HPA)."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
from genlib import level

W = "world-15-last-gaps"
ECHO = "hashicorp/http-echo:1.0"


def reset(n, *files):
    moves = "; ".join(f'[ -e "$W/{f}" ] && mv -f "$W/{f}" "$W/{f}.old"' for f in files)
    return f'W="$(cq_work_dir {n})"; {moves}; true'


# 129 ---------------------------------------------------------------------------------------------
level(W, "level-129-kubectl-debug", dict(
    name="No Shell, No Problem",
    description="The container has no shell and the node is far away. Debug both anyway",
    objective="Use kubectl debug with an ephemeral container and on a node",
    xp=300, difficulty="intermediate", expected_time="10m", domain="troubleshooting", course_section=14,
    namespace="debug-lab", concepts=["kubectl debug", "ephemeral containers", "--target", "node debugging"],
    task="""Pod **api** in namespace **debug-lab** runs an image without a shell. `kubectl exec api -- sh` fails.

1. Use `kubectl debug` to add an ephemeral `busybox:1.36` container to pod **api** that shares the process namespace of container **api**. Read the value of the environment variable **API_TOKEN** of the running api process and write it to `~/ckaquest-work/129/token.txt`.
2. Use `kubectl debug` on node **node01** (image `busybox:1.36`, namespace **debug-lab**). Write the kubelet's `staticPodPath` from node01's `/var/lib/kubelet/config.yaml` to `~/ckaquest-work/129/staticpodpath.txt`.""",
    docs=["https://kubernetes.io/docs/tasks/debug/debug-application/debug-running-pod/#ephemeral-container",
          "https://kubernetes.io/docs/tasks/debug/debug-cluster/kubectl-node-debug/"]),
    setup=reset(129, "token.txt", "staticpodpath.txt") + f"""
kubectl create secret generic api-token -n debug-lab --from-literal=token="$(openssl rand -hex 8)" >/dev/null
cat <<'EOF' | kubectl apply -f - >/dev/null
apiVersion: v1
kind: Pod
metadata:
  name: api
  namespace: debug-lab
spec:
  containers:
  - name: api
    image: {ECHO}
    args: ["-text=api", "-listen=:5678"]
    env:
    - name: API_TOKEN
      valueFrom:
        secretKeyRef:
          name: api-token
          key: token
EOF
kubectl wait --for=condition=Ready pod/api -n debug-lab --timeout=120s >/dev/null 2>&1 || true""",
    validate=r"""N1="$(cq_node_name node01)"
token() { jp debug-lab secret/api-token '{.data.token}' | base64 -d; }
node_dbg() { kubectl get pods -n debug-lab -o jsonpath='{range .items[*]}{.metadata.name} {.spec.nodeName}{"\n"}{end}' | grep -q "^node-debugger-.* $N1$"; }
check 2 "pod api has an ephemeral container targeting container api" field_eq debug-lab pod/api '{.spec.ephemeralContainers[0].targetContainerName}' api
check 2 "token.txt holds the API_TOKEN value" out_eq "$(token)" cat "$CQ_WORK/129/token.txt"
check "a node-debugger pod ran on node01" node_dbg
check 2 "staticpodpath.txt is /etc/kubernetes/manifests" out_eq /etc/kubernetes/manifests cat "$CQ_WORK/129/staticpodpath.txt" """,
    solve=r"""kubectl debug api -n debug-lab --image=busybox:1.36 --target=api -c dbg -- sleep 3600 >/dev/null
running() { kubectl get pod api -n debug-lab -o jsonpath='{.status.ephemeralContainerStatuses[0].state.running}' | grep -q .; }
cq_wait 90 running
kubectl exec api -n debug-lab -c dbg -- sh -c 'tr "\0" "\n" < /proc/1/environ' | sed -n 's/^API_TOKEN=//p' > "$CQ_WORK/129/token.txt"
N1="$(cq_node_name node01)"
pod="$(kubectl debug "node/$N1" -n debug-lab --image=busybox:1.36 -- cat /host/var/lib/kubelet/config.yaml | sed -n 's/.*pod\/\([^ ]*\).*/\1/p' | head -1)"
[ -n "$pod" ] || pod="$(kubectl get pods -n debug-lab -o name | grep node-debugger | head -1 | cut -d/ -f2)"
done_() { kubectl get pod "$pod" -n debug-lab -o jsonpath='{.status.phase}' | grep -q Succeeded; }
cq_wait 90 done_
kubectl logs "$pod" -n debug-lab | sed -n 's/^staticPodPath: *//p' > "$CQ_WORK/129/staticpodpath.txt" """,
    hints=["`k debug -h` lists the examples. For a pod: `--image`, `--target=<container>` to share its processes.",
           "In the debug container the api process is PID 1. `cat /proc/1/environ | tr '\\0' '\\n'` prints its environment.",
           "For the node: `k debug node/<node01 name> -n debug-lab -it --image=busybox:1.36`. The node's filesystem is mounted at `/host`."],
    solution="""```bash
k debug api -n debug-lab -it --image=busybox:1.36 --target=api -- sh
# inside:
tr '\\0' '\\n' < /proc/1/environ | grep API_TOKEN
exit
echo <value> > ~/ckaquest-work/129/token.txt

k get nodes                                        # node01's real name
k debug node/<node01> -n debug-lab -it --image=busybox:1.36
# inside:
grep staticPodPath /host/var/lib/kubelet/config.yaml
exit
echo /etc/kubernetes/manifests > ~/ckaquest-work/129/staticpodpath.txt
```""",
    debrief="""# No Shell, No Problem

## What happened
Minimal images (distroless, scratch) have no shell, so `kubectl exec` has nothing to run. `kubectl debug` adds an **ephemeral container** to the running pod. With `--target=<container>` it joins that container's process namespace, so you see its processes, their environment (`/proc/<pid>/environ`) and their files (`/proc/<pid>/root`).

Ephemeral containers cannot be removed. They stay in the pod spec until the pod is deleted.

## Node debugging
`kubectl debug node/<name>` starts a pod on that node with the host's namespaces and the node's root filesystem at `/host`. It is the answer when ssh is not available. `chroot /host` gives you the node's own tools.

## Other modes
- `--copy-to=<new pod>`: a copy of the pod you can change, for example `--set-image` or a different command.
- `--profile=general|baseline|restricted|sysadmin`: how many privileges the debug container gets.

## Exam angle
- `kubectl debug` is part of "troubleshoot clusters and nodes". Know the three forms: ephemeral, copy, node.

Bookmark: https://kubernetes.io/docs/tasks/debug/debug-application/debug-running-pod/

Your notes: Troubleshooting""")

# 130 ---------------------------------------------------------------------------------------------
NP_HEAD = """apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: {name}
  namespace: np-pick
spec:
  podSelector:
    matchLabels:
      app: backend
  policyTypes: ["Ingress"]
  ingress:
"""
NP_FILES = {
    "policy-1.yaml": ("allow-any-namespace", """  - from:
    - namespaceSelector: {}
    ports:
    - protocol: TCP
      port: 8080
"""),
    "policy-2.yaml": ("allow-frontend-all-ports", """  - from:
    - podSelector:
        matchLabels:
          app: frontend
"""),
    "policy-3.yaml": ("allow-frontend-8080", """  - from:
    - podSelector:
        matchLabels:
          app: frontend
    ports:
    - protocol: TCP
      port: 8080
"""),
    "policy-4.yaml": ("allow-everyone", """  - {}
"""),
    "policy-5.yaml": ("allow-front-8080", """  - from:
    - podSelector:
        matchLabels:
          app: front
    ports:
    - protocol: TCP
      port: 8080
"""),
}
np_writes = "\n".join(
    f"cat > \"$W/{f}\" <<'EOF'\n{NP_HEAD.format(name=name)}{body}EOF" for f, (name, body) in NP_FILES.items())

level(W, "level-130-least-permissive-policy", dict(
    name="Pick the Right Key",
    description="Five candidate NetworkPolicies, only one is right",
    objective="Read several NetworkPolicies and apply the least permissive one that works",
    xp=250, difficulty="intermediate", expected_time="7m", domain="networking", course_section=7,
    namespace="np-pick", concepts=["NetworkPolicy", "podSelector", "namespaceSelector", "ports", "least privilege"],
    task="""Namespace **np-pick** has pods **frontend**, **backend** and **other**, and a default deny-all ingress policy. **frontend** must reach **backend** on TCP port **8080**.

`~/ckaquest-work/130/` has five candidate policies. Apply **exactly one**: the least permissive policy that still lets frontend reach backend on 8080. Do not edit the files, and do not delete `deny-all`.""",
    docs=["https://kubernetes.io/docs/concepts/services-networking/network-policies/"]),
    setup=r"""W="$(cq_work_dir 130)"
""" + np_writes + f"""
cat <<'EOF' | kubectl apply -f - >/dev/null
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all
  namespace: np-pick
spec:
  podSelector: {{}}
  policyTypes: ["Ingress"]
EOF
kubectl run backend -n np-pick --image={ECHO} --labels=app=backend --port=8080 -- -text=backend -listen=:8080 >/dev/null
kubectl expose pod backend -n np-pick --port=8080 >/dev/null
kubectl run frontend -n np-pick --image=busybox:1.36 --labels=app=frontend -- sleep 3600 >/dev/null
kubectl run other -n np-pick --image=busybox:1.36 --labels=app=other -- sleep 3600 >/dev/null
kubectl wait --for=condition=Ready pod --all -n np-pick --timeout=120s >/dev/null 2>&1 || true""",
    validate=r"""from() { kubectl exec "$1" -n np-pick -- wget -qO- -T 3 http://backend:8080 2>/dev/null | grep -q backend; }
policies() { kubectl get netpol -n np-pick -o jsonpath='{range .items[*]}{.metadata.name}{"\n"}{end}' | sort | paste -sd' '; }
check 3 "only deny-all and allow-frontend-8080 are applied" out_eq "allow-frontend-8080 deny-all" policies
check "frontend reaches backend on 8080" from frontend
check "other is still blocked" bash -c "! kubectl exec other -n np-pick -- wget -qO- -T 3 http://backend:8080 >/dev/null 2>&1" """,
    solve=r"""kubectl apply -f "$CQ_WORK/130/policy-3.yaml"
sleep 5""",
    hints=["Read every file. Ask three questions: who may connect (from), on which ports, and to which pods.",
           "An empty `from` entry (`- {}`) or a `namespaceSelector: {}` allows far more than the frontend pod. A rule without `ports` allows every port.",
           "A selector that matches no pod (check the labels with `k get pods -n np-pick --show-labels`) blocks frontend. That is too strict, not least permissive."],
    solution="""```bash
k get pods -n np-pick --show-labels
cat ~/ckaquest-work/130/policy-*.yaml
# 1: every pod in every namespace         too open
# 2: frontend, but all ports               too open
# 3: frontend, TCP 8080                    right
# 4: everyone                              too open
# 5: label app=front matches nothing       frontend blocked
k apply -f ~/ckaquest-work/130/policy-3.yaml
k exec frontend -n np-pick -- wget -qO- -T 3 http://backend:8080
```""",
    debrief="""# Pick the Right Key

## What happened
NetworkPolicies are allow lists. Once a pod is selected by any policy for Ingress, only traffic that some policy allows gets in. Policies add up. They never subtract.

So "least permissive" means: the smallest set of sources and ports that still makes the required connection work.

## Reading a rule
- `podSelector` in `spec`: which pods the policy protects.
- `from.podSelector`: pods in the **same** namespace.
- `from.namespaceSelector: {}`: every pod in every namespace.
- `- {}` as an ingress rule: everything.
- no `ports`: all ports.
- `podSelector` and `namespaceSelector` in the **same** `from` item: AND. As two items: OR.

## Exam angle
- Reported: "several policy files are given, apply the least permissive one". Read them all before applying anything. Applying a wrong one and then a right one leaves both active.

Bookmark: https://kubernetes.io/docs/concepts/services-networking/network-policies/

Your notes: Network Policies""")

# 131 ---------------------------------------------------------------------------------------------
level(W, "level-131-aggregated-clusterrole", dict(
    name="Roles That Grow by Themselves",
    description="The monitoring team wants one role that collects permissions from others",
    objective="Build an aggregated ClusterRole and bind it to a ServiceAccount",
    xp=250, difficulty="intermediate", expected_time="8m", domain="architecture", course_section=7,
    namespace="agg-lab", concepts=["ClusterRole aggregation", "aggregationRule", "ClusterRoleBinding", "ServiceAccount"],
    task="""1. Create ClusterRole **monitoring** with no rules of its own. It must aggregate every ClusterRole labeled `rbac.ckaquest.io/aggregate-to-monitoring: "true"`.
2. Create ClusterRole **monitoring-pods** with that label: `get`, `list`, `watch` on pods.
3. Create ClusterRole **monitoring-nodes** with that label: `get`, `list` on nodes.
4. Bind ClusterRole **monitoring** to ServiceAccount **monitor** in namespace **agg-lab** with ClusterRoleBinding **monitoring**.""",
    docs=["https://kubernetes.io/docs/reference/access-authn-authz/rbac/#aggregated-clusterroles"]),
    setup=r"""kubectl delete clusterrole monitoring monitoring-pods monitoring-nodes --ignore-not-found >/dev/null 2>&1
kubectl delete clusterrolebinding monitoring --ignore-not-found >/dev/null 2>&1
kubectl create serviceaccount monitor -n agg-lab >/dev/null""",
    validate=r"""SA=system:serviceaccount:agg-lab:monitor
check 2 "monitoring aggregates the label rbac.ckaquest.io/aggregate-to-monitoring" field_eq - clusterrole/monitoring '{.aggregationRule.clusterRoleSelectors[0].matchLabels.rbac\.ckaquest\.io/aggregate-to-monitoring}' true
check "monitoring-pods and monitoring-nodes carry the label" out_eq "monitoring-nodes monitoring-pods" bash -c "kubectl get clusterrole -l rbac.ckaquest.io/aggregate-to-monitoring=true -o name | cut -d/ -f2 | sort | paste -sd' '"
check "ClusterRoleBinding monitoring binds monitoring to agg-lab/monitor" out_eq "monitoring ServiceAccount monitor agg-lab" kubectl get clusterrolebinding monitoring -o jsonpath='{.roleRef.name} {.subjects[0].kind} {.subjects[0].name} {.subjects[0].namespace}'
check 2 "monitor can list pods in all namespaces" can_i "$SA" list pods
check "monitor can list nodes" can_i "$SA" list nodes
check "monitor cannot delete pods" cannot_i "$SA" delete pods""",
    solve=r"""cat <<'EOF' | kubectl apply -f -
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: monitoring
aggregationRule:
  clusterRoleSelectors:
  - matchLabels:
      rbac.ckaquest.io/aggregate-to-monitoring: "true"
rules: []
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: monitoring-pods
  labels:
    rbac.ckaquest.io/aggregate-to-monitoring: "true"
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list", "watch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: monitoring-nodes
  labels:
    rbac.ckaquest.io/aggregate-to-monitoring: "true"
rules:
- apiGroups: [""]
  resources: ["nodes"]
  verbs: ["get", "list"]
EOF
kubectl create clusterrolebinding monitoring --clusterrole=monitoring --serviceaccount=agg-lab:monitor
sleep 3""",
    cleanup="""kubectl delete clusterrole monitoring monitoring-pods monitoring-nodes --ignore-not-found >/dev/null 2>&1
kubectl delete clusterrolebinding monitoring --ignore-not-found >/dev/null 2>&1""",
    hints=["The RBAC docs page has an example under **Aggregated ClusterRoles**.",
           "`aggregationRule.clusterRoleSelectors[].matchLabels` picks the roles. The controller fills `rules` for you, so leave them empty.",
           "`k create clusterrole monitoring-pods --verb=get,list,watch --resource=pods`, then `k label clusterrole monitoring-pods rbac.ckaquest.io/aggregate-to-monitoring=true`."],
    solution="""```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: monitoring
aggregationRule:
  clusterRoleSelectors:
  - matchLabels:
      rbac.ckaquest.io/aggregate-to-monitoring: "true"
rules: []
```

```bash
k apply -f monitoring.yaml
k create clusterrole monitoring-pods --verb=get,list,watch --resource=pods
k create clusterrole monitoring-nodes --verb=get,list --resource=nodes
k label clusterrole monitoring-pods monitoring-nodes rbac.ckaquest.io/aggregate-to-monitoring=true
k create clusterrolebinding monitoring --clusterrole=monitoring --serviceaccount=agg-lab:monitor
k get clusterrole monitoring -o yaml        # rules are filled in
k auth can-i list nodes --as=system:serviceaccount:agg-lab:monitor
```""",
    debrief="""# Roles That Grow by Themselves

## What happened
An aggregated ClusterRole has an `aggregationRule` instead of its own rules. A controller in kube-controller-manager watches for ClusterRoles that match the label selector and copies their rules into the aggregated role. Add a new labeled role later and everyone bound to the aggregate gets it at once.

## Where you have seen this
The built-in `admin`, `edit` and `view` roles are aggregated. A CRD author adds `rbac.authorization.k8s.io/aggregate-to-view: "true"` to a ClusterRole, and every user with `view` can read the new resource.

## Gotchas
- Rules you write by hand into an aggregated role are overwritten by the controller.
- `k auth can-i ... --as=system:serviceaccount:<ns>:<name>` checks a ServiceAccount.

## Exam angle
- Know `aggregationRule` and the `aggregate-to-*` labels. Creating the parts imperatively and labeling them afterwards is fastest.

Bookmark: https://kubernetes.io/docs/reference/access-authn-authz/rbac/#aggregated-clusterroles

Your notes: RBAC""")

# 132 ---------------------------------------------------------------------------------------------
level(W, "level-132-endpointslice-by-hand", dict(
    name="A Service Without a Selector",
    description="The legacy backend is not something a selector can find",
    objective="Create a selectorless Service and its EndpointSlice by hand",
    xp=250, difficulty="intermediate", expected_time="8m", domain="networking", course_section=9,
    namespace="ext-lab", concepts=["Service without selector", "EndpointSlice", "kubernetes.io/service-name"],
    task="""Pod **legacy-backend** in namespace **legacy-host** answers on port **5678**. Apps in **ext-lab** must reach it as `legacy.ext-lab:80`, but nobody may add labels to it or touch namespace legacy-host.

1. Create Service **legacy** in **ext-lab** **without a selector**, with port **80** named **http**.
2. Create EndpointSlice **legacy-1** in **ext-lab** for that Service. Address type IPv4, one endpoint with the current IP of pod legacy-backend, port **5678** named **http**.
3. `http://legacy.ext-lab` must answer from inside the cluster.""",
    docs=["https://kubernetes.io/docs/concepts/services-networking/service/#services-without-selectors",
          "https://kubernetes.io/docs/concepts/services-networking/endpoint-slices/"]),
    setup=f"""kubectl delete ns legacy-host --ignore-not-found --wait=true >/dev/null 2>&1
kubectl create ns legacy-host >/dev/null
kubectl run legacy-backend -n legacy-host --image={ECHO} --port=5678 -- -text="legacy backend" -listen=:5678 >/dev/null
kubectl wait --for=condition=Ready pod/legacy-backend -n legacy-host --timeout=120s >/dev/null 2>&1 || true""",
    validate=r"""ip() { kubectl get pod legacy-backend -n legacy-host -o jsonpath='{.status.podIP}'; }
reach() { in_cluster_out ext-lab curlimages/curl:8.11.1 curl -s -m 5 http://legacy.ext-lab | grep -q "legacy backend"; }
check "Service legacy has no selector" field_eq ext-lab svc/legacy '{.spec.selector}' ""
check "Service port 80 is named http" out_eq "http 80" kubectl get svc legacy -n ext-lab -o jsonpath='{.spec.ports[0].name} {.spec.ports[0].port}'
check 2 "EndpointSlice legacy-1 belongs to Service legacy" field_eq ext-lab endpointslice/legacy-1 '{.metadata.labels.kubernetes\.io/service-name}' legacy
check "it points at the backend pod's IP, port http 5678" out_eq "IPv4 $(ip) http 5678" kubectl get endpointslice legacy-1 -n ext-lab -o jsonpath='{.addressType} {.endpoints[0].addresses[0]} {.ports[0].name} {.ports[0].port}'
check 3 "http://legacy.ext-lab answers 'legacy backend'" reach""",
    solve=r"""IP="$(kubectl get pod legacy-backend -n legacy-host -o jsonpath='{.status.podIP}')"
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Service
metadata:
  name: legacy
  namespace: ext-lab
spec:
  ports:
  - name: http
    port: 80
    protocol: TCP
---
apiVersion: discovery.k8s.io/v1
kind: EndpointSlice
metadata:
  name: legacy-1
  namespace: ext-lab
  labels:
    kubernetes.io/service-name: legacy
addressType: IPv4
ports:
- name: http
  port: 5678
  protocol: TCP
endpoints:
- addresses: ["$IP"]
EOF
sleep 5""",
    cleanup="kubectl delete ns legacy-host --ignore-not-found --wait=false >/dev/null 2>&1",
    hints=["`k get pod legacy-backend -n legacy-host -o wide` gives the IP.",
           "A Service without `selector` gets no endpoints. You provide them. The docs page for Service has the example under **Services without selectors**.",
           "The EndpointSlice needs the label `kubernetes.io/service-name: legacy`. Its port **name** must match the Service port name (`http`). The number is the backend's port (5678)."],
    solution="""```yaml
apiVersion: v1
kind: Service
metadata:
  name: legacy
  namespace: ext-lab
spec:
  ports:
  - name: http
    port: 80
---
apiVersion: discovery.k8s.io/v1
kind: EndpointSlice
metadata:
  name: legacy-1
  namespace: ext-lab
  labels:
    kubernetes.io/service-name: legacy
addressType: IPv4
ports:
- name: http
  port: 5678
endpoints:
- addresses: ["<pod IP>"]
```

```bash
k get pod legacy-backend -n legacy-host -o wide
k apply -f legacy.yaml
k run t -n ext-lab --rm -it --image=curlimages/curl:8.11.1 --restart=Never -- curl -s http://legacy.ext-lab
```""",
    debrief="""# A Service Without a Selector

## What happened
Normally the EndpointSlice controller watches the Service's selector and writes the matching pod IPs into EndpointSlices. Without a selector, nothing does that. You write the EndpointSlice yourself and kube-proxy routes to whatever addresses it lists.

kube-proxy connects the two by the label `kubernetes.io/service-name` and by the **port name**. The Service port 80 named `http` sends traffic to the slice port named `http`, here 5678.

## When to use it
- A database outside the cluster, or in another cluster.
- Moving a workload into Kubernetes step by step.
- `type: ExternalName` is the DNS-only alternative. It returns a CNAME and has no ports.

## Gotchas
- The IP is static. If the pod restarts with a new IP, the slice is stale.
- The older `Endpoints` object still works but is deprecated. Use `EndpointSlice`.

## Exam angle
- "Use ClusterIP, NodePort, LoadBalancer service types and **endpoints**" is in the curriculum. A selectorless Service is the classic endpoints task.

Bookmark: https://kubernetes.io/docs/concepts/services-networking/service/#services-without-selectors

Your notes: Services""")

# 133 ---------------------------------------------------------------------------------------------
level(W, "level-133-hpa-two-metrics", dict(
    name="Scale on Two Signals",
    description="The API is memory hungry as well as CPU hungry",
    objective="Create an autoscaling/v2 HPA with a CPU and a memory metric",
    xp=250, difficulty="intermediate", expected_time="7m", domain="workloads", course_section=5,
    namespace="hpa-multi", concepts=["HorizontalPodAutoscaler v2", "Utilization", "AverageValue", "multiple metrics"],
    task="""Deployment **api** in namespace **hpa-multi** has CPU and memory requests.

Create HPA **api** for it:
- min **2**, max **6** replicas
- CPU: average utilization **60%**
- memory: average value **50Mi** per pod (an absolute value, not a percentage)

The HPA must read both metrics.""",
    docs=["https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale-walkthrough/#autoscaling-on-multiple-metrics-and-custom-metrics",
          "https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/"]),
    setup=r"""cat <<'EOF' | kubectl apply -f - >/dev/null
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
  namespace: hpa-multi
spec:
  replicas: 1
  selector:
    matchLabels:
      app: api
  template:
    metadata:
      labels:
        app: api
    spec:
      containers:
      - name: api
        image: nginx:1.27
        resources:
          requests:
            cpu: 100m
            memory: 64Mi
EOF
kubectl rollout status deploy/api -n hpa-multi --timeout=120s >/dev/null 2>&1 || true""",
    validate=r"""M='{.spec.metrics'
metric() { kubectl get hpa api -n hpa-multi -o jsonpath="$M[?(@.resource.name==\"$1\")].resource.target.type} $M[?(@.resource.name==\"$1\")].resource.target.$2}"; }
reading() { [ "$(kubectl get hpa api -n hpa-multi -o jsonpath='{range .status.currentMetrics[*]}{.resource.name}{"\n"}{end}' | sort | paste -sd' ')" = "cpu memory" ]; }
check "HPA api targets Deployment api, 2 to 6" out_eq "Deployment api 2 6" kubectl get hpa api -n hpa-multi -o jsonpath='{.spec.scaleTargetRef.kind} {.spec.scaleTargetRef.name} {.spec.minReplicas} {.spec.maxReplicas}'
check 2 "CPU: Utilization 60" out_eq "Utilization 60" metric cpu averageUtilization
check 2 "memory: AverageValue 50Mi" out_eq "AverageValue 50Mi" metric memory averageValue
check 2 "the HPA reads current CPU and memory" reading""",
    solve=r"""cat <<'EOF' | kubectl apply -f -
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api
  namespace: hpa-multi
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api
  minReplicas: 2
  maxReplicas: 6
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 60
  - type: Resource
    resource:
      name: memory
      target:
        type: AverageValue
        averageValue: 50Mi
EOF
reading() { [ "$(kubectl get hpa api -n hpa-multi -o jsonpath='{range .status.currentMetrics[*]}{.resource.name}{"\n"}{end}' | sort | paste -sd' ')" = "cpu memory" ]; }
cq_wait 180 reading""",
    hints=["`k autoscale` only does CPU. Start from it with `$do`, then add the memory metric by hand.",
           "Each entry in `metrics` is `type: Resource` with `resource.name` and a `target`. CPU uses `type: Utilization` with `averageUtilization`. Memory here uses `type: AverageValue` with `averageValue: 50Mi`.",
           "`k describe hpa api -n hpa-multi` shows both current values once metrics-server has data, after about a minute."],
    solution="""```bash
k autoscale deploy api -n hpa-multi --min=2 --max=6 --cpu=60% $do > hpa.yaml
```

```yaml
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 60
  - type: Resource
    resource:
      name: memory
      target:
        type: AverageValue
        averageValue: 50Mi
```

```bash
k apply -f hpa.yaml
k describe hpa api -n hpa-multi
```""",
    debrief="""# Scale on Two Signals

## What happened
With several metrics the HPA computes a desired replica count for each one and takes the **highest**. So either signal alone can scale the Deployment up.

## Target types
- `Utilization`: percent of the pod's **request**. Only for `Resource` metrics, and the containers need requests.
- `AverageValue`: an absolute value per pod, like `50Mi` or `200m`.
- `Value`: one absolute value for the whole target. Used with `Object` and `External` metrics.

## Metric sources
- `Resource` (cpu, memory): from metrics-server.
- `ContainerResource`: one container of the pod, ignores sidecars.
- `Pods`, `Object`, `External`: custom metrics. They need an adapter such as prometheus-adapter or KEDA. Without one the HPA shows `<unknown>`.

## Exam angle
- `k autoscale` writes CPU only. Know the v2 YAML for memory and for a second metric.

Bookmark: https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale-walkthrough/

Your notes: Autoscaling""")
