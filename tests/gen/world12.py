"""Writes World 12 (speed drills: JSONPath, custom-columns, sort-by, imperative, $do)."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
from genlib import level

W = "world-12-drills"
CHEAT = "https://kubernetes.io/docs/reference/kubectl/quick-reference/"
JSONPATH = "https://kubernetes.io/docs/reference/kubectl/jsonpath/"
SAME = """same() { diff <(sed -e 's/[[:space:]]\\+/ /g' -e 's/ $//' "$1" | sed '/^$/d') <(eval "$2" | sed -e 's/[[:space:]]\\+/ /g' -e 's/ $//' | sed '/^$/d') >/dev/null 2>&1; }
same_sorted() { diff <(sed -e 's/[[:space:]]\\+/ /g' -e 's/ $//' "$1" | sed '/^$/d' | sort) <(eval "$2" | sed -e 's/[[:space:]]\\+/ /g' -e 's/ $//' | sed '/^$/d' | sort) >/dev/null 2>&1; }"""


def reset(n):
    return f'W="$(cq_work_dir {n})"; for f in "$W"/*; do [ -e "$f" ] && mv -f "$f" "$f.old"; done; true'


def pods(ns, specs):
    out = []
    for name, image, labels in specs:
        out.append(f"kubectl run {name} -n {ns} --image={image} --labels={labels} >/dev/null")
    out.append(f"kubectl wait --for=condition=Ready pod --all -n {ns} --timeout=120s >/dev/null 2>&1 || true")
    return "\n".join(out)


level(W, "level-103-jsonpath-nodes", dict(
    name="Drill: Node IPs",
    description="JSONPath range over nodes",
    objective="Write every node name with its internal IP using JSONPath",
    xp=150, difficulty="intermediate", expected_time="3m", domain="architecture", course_section=2,
    namespace="drills", concepts=["jsonpath", "range", "filters"],
    task="""Write one line per node to `~/ckaquest-work/103/nodes.txt`: the node name, a space, and its **InternalIP**.

Use kubectl with JSONPath. Par time: 3 minutes.""",
    docs=[JSONPATH, CHEAT]),
    setup=reset(103),
    validate=SAME + """
EXP="kubectl get nodes -o jsonpath='{range .items[*]}{.metadata.name} {.status.addresses[?(@.type==\\"InternalIP\\")].address}{\\"\\\\n\\"}{end}'"
check 3 "nodes.txt has name and InternalIP for every node" same_sorted "$CQ_WORK/103/nodes.txt" "$EXP\"""",
    solve="""kubectl get nodes -o jsonpath='{range .items[*]}{.metadata.name} {.status.addresses[?(@.type=="InternalIP")].address}{"\\n"}{end}' > "$CQ_WORK/103/nodes.txt\"""",
    hints=["`{range .items[*]}...{end}` loops. `{\"\\n\"}` adds a newline.", "A filter: `.status.addresses[?(@.type==\"InternalIP\")].address`.", "Test on screen first, then redirect with `>`."],
    solution="""```bash
k get nodes -o jsonpath='{range .items[*]}{.metadata.name} {.status.addresses[?(@.type=="InternalIP")].address}{"\\n"}{end}' > ~/ckaquest-work/103/nodes.txt
```""",
    debrief="""# Drill: Node IPs

## Pattern
`{range .items[*]}<fields>{"\\n"}{end}` is the template for one line per object. Filters `[?(@.key=="value")]` pick one element of a list.

## Exam angle
- The kubectl quick reference page has many JSONPath examples. Search it for "jsonpath".
- `-o wide` shows INTERNAL-IP too, but the task asks for an exact format.

Bookmark: https://kubernetes.io/docs/reference/kubectl/jsonpath/

Your notes: JSONPath""")

level(W, "level-104-custom-columns", dict(
    name="Drill: Custom Columns",
    description="A table with exactly the columns ops asked for",
    objective="Use custom-columns and sort-by",
    xp=150, difficulty="intermediate", expected_time="3m", domain="architecture", course_section=2,
    namespace="drill-104", concepts=["custom-columns", "--sort-by"],
    task="""Write a table of all pods in namespace **drill-104** to `~/ckaquest-work/104/pods.txt` with the columns **POD**, **IMAGE** and **NODE** (pod name, image of the first container, node name), sorted by pod name.

Par time: 3 minutes.""",
    docs=["https://kubernetes.io/docs/reference/kubectl/#custom-columns", CHEAT]),
    setup=reset(104) + """
kubectl run zeta -n drill-104 --image=nginx:1.27-alpine >/dev/null
kubectl run alpha -n drill-104 --image=busybox:1.36 -- sleep 3600 >/dev/null
kubectl run mike -n drill-104 --image=nginx:1.28-alpine >/dev/null
kubectl wait --for=condition=Ready pod --all -n drill-104 --timeout=120s >/dev/null 2>&1 || true""",
    validate=SAME + """
EXP="kubectl get pods -n drill-104 --sort-by=.metadata.name -o custom-columns=POD:.metadata.name,IMAGE:.spec.containers[0].image,NODE:.spec.nodeName"
check 3 "pods.txt matches the expected table" same "$CQ_WORK/104/pods.txt" "$EXP\"""",
    solve="""sleep 5
kubectl get pods -n drill-104 --sort-by=.metadata.name -o custom-columns=POD:.metadata.name,IMAGE:.spec.containers[0].image,NODE:.spec.nodeName > "$CQ_WORK/104/pods.txt\"""",
    hints=["`-o custom-columns=HEADER:jsonpath,HEADER:jsonpath`. No spaces after the commas.", "`--sort-by=.metadata.name`", "Image of the first container: `.spec.containers[0].image`."],
    solution="""```bash
k get pods -n drill-104 --sort-by=.metadata.name \\
  -o custom-columns=POD:.metadata.name,IMAGE:.spec.containers[0].image,NODE:.spec.nodeName > ~/ckaquest-work/104/pods.txt
```""",
    debrief="""# Drill: Custom Columns

## Pattern
`-o custom-columns=NAME:.path,...` and `--sort-by=.path`. The path starts at the object, not at `.items`.

## Exam angle
- Header names are what the task says, in capitals.
- `--sort-by` works with any `-o` format.

Bookmark: https://kubernetes.io/docs/reference/kubectl/#custom-columns

Your notes: kubectl Cheat Sheet, JSONPath""")

level(W, "level-105-sort-pv", dict(
    name="Drill: Sort by Capacity",
    description="Which volumes are the biggest?",
    objective="Sort cluster-scoped objects by a nested field",
    xp=150, difficulty="intermediate", expected_time="3m", domain="storage", course_section=8,
    namespace="drills", concepts=["--sort-by", "PersistentVolumes", "jsonpath"],
    task="""The cluster has PersistentVolumes whose names start with **drill-pv-**.

Write their names, one per line, sorted by capacity from **smallest to largest**, to `~/ckaquest-work/105/pvs.txt`. Only the drill-pv volumes.

Par time: 3 minutes.""",
    docs=[CHEAT]),
    setup=reset(105) + """
for s in 3Gi:a 500Mi:b 10Gi:c 1Gi:d; do
cat <<EOF | kubectl apply -f - >/dev/null
apiVersion: v1
kind: PersistentVolume
metadata:
  name: drill-pv-${s#*:}
spec:
  capacity: {storage: ${s%:*}}
  accessModes: [ReadWriteOnce]
  storageClassName: drill
  hostPath: {path: /tmp/drill-pv}
EOF
done""",
    validate="""want="$(printf 'drill-pv-b\\ndrill-pv-d\\ndrill-pv-a\\ndrill-pv-c')"
check 3 "pvs.txt lists b, d, a, c" out_eq "$want" sh -c "sed -e 's/[[:space:]]*$//' -e '/^$/d' '$CQ_WORK/105/pvs.txt'\"""",
    solve="""kubectl get pv --sort-by=.spec.capacity.storage -o jsonpath='{range .items[*]}{.metadata.name}{"\\n"}{end}' | grep '^drill-pv-' > "$CQ_WORK/105/pvs.txt\"""",
    cleanup="kubectl delete pv drill-pv-a drill-pv-b drill-pv-c drill-pv-d --ignore-not-found --wait=false >/dev/null 2>&1",
    hints=["`--sort-by=.spec.capacity.storage` understands quantities (500Mi < 1Gi).", "Print only names: `-o name` gives `persistentvolume/...`, JSONPath gives the bare name.", "Filter with `grep '^drill-pv-'`."],
    solution="""```bash
k get pv --sort-by=.spec.capacity.storage -o jsonpath='{range .items[*]}{.metadata.name}{"\\n"}{end}' \\
  | grep '^drill-pv-' > ~/ckaquest-work/105/pvs.txt
```""",
    debrief="""# Drill: Sort by Capacity

## Pattern
`--sort-by` compares quantities correctly, so 500Mi sorts before 1Gi. Then filter with grep or a label selector.

## Exam angle
- "Sort PVs by capacity" and "sort pods by creation time" (`--sort-by=.metadata.creationTimestamp`) are classic.

Bookmark: https://kubernetes.io/docs/reference/kubectl/quick-reference/

Your notes: kubectl Cheat Sheet""")

level(W, "level-106-imperative-blitz", dict(
    name="Drill: Imperative Blitz",
    description="Eight objects, no YAML editor",
    objective="Create common objects with imperative kubectl only",
    xp=200, difficulty="intermediate", expected_time="5m", domain="workloads", course_section=2,
    namespace="drill-106", concepts=["kubectl run", "create deployment", "expose", "create configmap/secret/sa/role/rolebinding"],
    task="""In namespace **drill-106**, using only imperative commands:
1. Pod **web**, image `nginx:1.27-alpine`, label `tier=web`
2. Deployment **api**, image `nginx:1.27-alpine`, 3 replicas
3. Service **api**, ClusterIP, port 80, for the Deployment api
4. ConfigMap **cfg** with `mode=fast`
5. Secret **token** with `t=abc123`
6. ServiceAccount **bot**
7. Role **pod-reader** (get, list on pods) and RoleBinding **bot-pod-reader** for bot

Par time: 5 minutes.""",
    docs=[CHEAT]),
    validate="""check "pod web with tier=web" field_eq drill-106 pod/web '{.metadata.labels.tier}' web
check "deployment api has 3 ready replicas" deploy_ready drill-106 api 3
check "service api selects the api pods" field_eq drill-106 svc/api '{.spec.selector.app}' api
check "configmap cfg mode=fast" field_eq drill-106 cm/cfg '{.data.mode}' fast
check "secret token t=abc123" out_eq abc123 sh -c "kubectl get secret token -n drill-106 -o jsonpath='{.data.t}' | base64 -d"
check "serviceaccount bot exists" exists drill-106 sa/bot
check 2 "bot can list pods, not delete them" sh -c "[ \\"\\$(kubectl auth can-i list pods -n drill-106 --as=system:serviceaccount:drill-106:bot)\\" = yes ] && [ \\"\\$(kubectl auth can-i delete pods -n drill-106 --as=system:serviceaccount:drill-106:bot)\\" = no ]\"""",
    solve="""N="-n drill-106"
kubectl run web $N --image=nginx:1.27-alpine -l tier=web
kubectl create deployment api $N --image=nginx:1.27-alpine --replicas=3
kubectl expose deployment api $N --port=80
kubectl create configmap cfg $N --from-literal=mode=fast
kubectl create secret generic token $N --from-literal=t=abc123
kubectl create serviceaccount bot $N
kubectl create role pod-reader $N --verb=get,list --resource=pods
kubectl create rolebinding bot-pod-reader $N --role=pod-reader --serviceaccount=drill-106:bot
kubectl rollout status deploy/api $N --timeout=90s""",
    hints=["Set the namespace once: `k config set-context --current --namespace=drill-106`. Set it back after.", "`k expose deploy api --port=80`", "`k create rolebinding ... --serviceaccount=drill-106:bot`"],
    solution="""```bash
k config set-context --current --namespace=drill-106
k run web --image=nginx:1.27-alpine -l tier=web
k create deploy api --image=nginx:1.27-alpine --replicas=3
k expose deploy api --port=80
k create cm cfg --from-literal=mode=fast
k create secret generic token --from-literal=t=abc123
k create sa bot
k create role pod-reader --verb=get,list --resource=pods
k create rolebinding bot-pod-reader --role=pod-reader --serviceaccount=drill-106:bot
k config set-context --current --namespace=default
```""",
    debrief="""# Drill: Imperative Blitz

## Why
In the exam every minute counts. Most objects have a `create` or `run` command that is faster than YAML, and less error-prone.

## No imperative command for
NetworkPolicy, PV, PVC, StatefulSet, DaemonSet, HTTPRoute, LimitRange. For those, copy from the docs or start from a `$do` output of something similar.

## Exam angle
- Switching namespace with `set-context` saves typing but is easy to forget. Switch back.

Bookmark: https://kubernetes.io/docs/reference/kubectl/quick-reference/

Your notes: Imperative vs Declarative, kubectl Cheat Sheet""")

level(W, "level-107-dry-run-yaml", dict(
    name="Drill: $do and Edit",
    description="Generate YAML, add what kubectl create cannot set, apply",
    objective="Use --dry-run=client -o yaml as a starting point",
    xp=150, difficulty="intermediate", expected_time="4m", domain="workloads", course_section=2,
    namespace="drill-107", concepts=["--dry-run=client -o yaml", "env", "resources", "probes"],
    task="""Save a Deployment manifest to `~/ckaquest-work/107/deploy.yaml` and apply it:
- Deployment **shop** in namespace **drill-107**, image `nginx:1.27-alpine`, 2 replicas
- env var `MODE=prod`
- requests CPU **50m**, memory **32Mi**
- readiness probe: HTTP GET `/` on port 80

Par time: 4 minutes.""",
    docs=[CHEAT, "https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/"]),
    setup=reset(107),
    validate="""C='{.spec.template.spec.containers[0]'
check "deploy.yaml exists and is a Deployment shop" file_contains "$CQ_WORK/107/deploy.yaml" "name: shop"
check "MODE=prod" field_eq drill-107 deploy/shop "$C.env[?(@.name==\\"MODE\\")].value}" prod
check "requests 50m / 32Mi" out_eq "50m 32Mi" kubectl get deploy shop -n drill-107 -o jsonpath="$C.resources.requests.cpu} $C.resources.requests.memory}"
check "readiness probe GET / on 80" out_eq "/ 80" kubectl get deploy shop -n drill-107 -o jsonpath="$C.readinessProbe.httpGet.path} $C.readinessProbe.httpGet.port}"
check 2 "shop has 2/2 ready replicas" deploy_ready drill-107 shop 2""",
    solve="""F="$CQ_WORK/107/deploy.yaml"
kubectl create deployment shop -n drill-107 --image=nginx:1.27-alpine --replicas=2 --dry-run=client -o yaml \\
 | "$CQ_ROOT/venv/bin/python3" -c '
import sys, yaml
d = yaml.safe_load(sys.stdin)
c = d["spec"]["template"]["spec"]["containers"][0]
c["env"] = [{"name": "MODE", "value": "prod"}]
c["resources"] = {"requests": {"cpu": "50m", "memory": "32Mi"}}
c["readinessProbe"] = {"httpGet": {"path": "/", "port": 80}}
print(yaml.safe_dump(d))' > "$F"
kubectl apply -f "$F"
kubectl rollout status deploy/shop -n drill-107 --timeout=90s""",
    hints=["`k create deploy shop -n drill-107 --image=nginx:1.27-alpine --replicas=2 $do > deploy.yaml`", "Add env, resources and readinessProbe under the container in vim.", "`k apply -f deploy.yaml`"],
    solution="""```bash
k create deploy shop -n drill-107 --image=nginx:1.27-alpine --replicas=2 $do > ~/ckaquest-work/107/deploy.yaml
vim ~/ckaquest-work/107/deploy.yaml
```

```yaml
      containers:
      - image: nginx:1.27-alpine
        name: nginx
        env:
        - {name: MODE, value: prod}
        resources:
          requests: {cpu: 50m, memory: 32Mi}
        readinessProbe:
          httpGet: {path: /, port: 80}
```""",
    debrief="""# Drill: $do and Edit

## Why
`$do` gives correct boilerplate in a second. You only type the parts kubectl cannot set.

## vim settings that help
`:set paste` before pasting from the docs, `:set nopaste` after. The node `.vimrc` here sets 2-space indents.

Bookmark: https://kubernetes.io/docs/reference/kubectl/quick-reference/

Your notes: YAML in Kubernetes, Imperative vs Declarative""")

level(W, "level-108-jsonpath-images", dict(
    name="Drill: Which Image Where",
    description="Security asks which sidecar image each shop pod runs",
    objective="JSONPath with a filter on container name",
    xp=150, difficulty="intermediate", expected_time="3m", domain="workloads", course_section=2,
    namespace="drill-108", concepts=["jsonpath filters", "label selectors"],
    task="""Pods with label `app=shop` in namespace **drill-108** have a container named **sidecar**.

Write one line per such pod to `~/ckaquest-work/108/sidecars.txt`: pod name, a space, the image of its **sidecar** container.

Par time: 3 minutes.""",
    docs=[JSONPATH]),
    setup=reset(108) + """
mk() {
cat <<EOF | kubectl apply -f - >/dev/null
apiVersion: v1
kind: Pod
metadata:
  name: $1
  namespace: drill-108
  labels: {app: $2}
spec:
  containers:
  - {name: main, image: nginx:1.27-alpine}
  - {name: sidecar, image: $3, command: [sleep, "3600"]}
EOF
}
mk shop-1 shop busybox:1.36
mk shop-2 shop busybox:1.37
mk blog-1 blog busybox:1.36""",
    validate=SAME + """
EXP="kubectl get pods -n drill-108 -l app=shop -o jsonpath='{range .items[*]}{.metadata.name} {.spec.containers[?(@.name==\\"sidecar\\")].image}{\\"\\\\n\\"}{end}'"
check 3 "sidecars.txt lists every shop pod with its sidecar image" same_sorted "$CQ_WORK/108/sidecars.txt" "$EXP\"""",
    solve="""kubectl get pods -n drill-108 -l app=shop -o jsonpath='{range .items[*]}{.metadata.name} {.spec.containers[?(@.name=="sidecar")].image}{"\\n"}{end}' > "$CQ_WORK/108/sidecars.txt\"""",
    hints=["`-l app=shop` limits the pods.", "Filter containers by name: `.spec.containers[?(@.name==\"sidecar\")].image`.", "Wrap it in `{range .items[*]}...{\"\\n\"}{end}`."],
    solution="""```bash
k get pods -n drill-108 -l app=shop \\
  -o jsonpath='{range .items[*]}{.metadata.name} {.spec.containers[?(@.name=="sidecar")].image}{"\\n"}{end}' \\
  > ~/ckaquest-work/108/sidecars.txt
```""",
    debrief="""# Drill: Which Image Where

## Pattern
Index by position (`containers[0]`) only when the task says "first container". Otherwise filter by name.

Bookmark: https://kubernetes.io/docs/reference/kubectl/jsonpath/

Your notes: JSONPath""")

level(W, "level-109-not-running", dict(
    name="Drill: What Is Not Running",
    description="Find every unhealthy pod across a set of namespaces",
    objective="Use field selectors across namespaces",
    xp=150, difficulty="intermediate", expected_time="3m", domain="troubleshooting", course_section=14,
    namespace="drill-109", concepts=["--field-selector", "-A", "status.phase"],
    task="""Across **all namespaces**, find the pods whose phase is **not Running** and **not Succeeded**.

Write them to `~/ckaquest-work/109/broken.txt`, one per line as `namespace/name`. Ignore pods in kube-system.

Par time: 3 minutes.""",
    docs=["https://kubernetes.io/docs/concepts/overview/working-with-objects/field-selectors/"]),
    setup=reset(109) + """
kubectl create ns drill-109b --dry-run=client -o yaml | kubectl apply -f - >/dev/null
kubectl run ok -n drill-109 --image=nginx:1.27-alpine >/dev/null
kubectl run badimage -n drill-109 --image=nginx:no-such-tag-cq >/dev/null
kubectl run toobig -n drill-109b --image=nginx:1.27-alpine --overrides='{"spec":{"containers":[{"name":"toobig","image":"nginx:1.27-alpine","resources":{"requests":{"cpu":"64"}}}]}}' >/dev/null
sleep 5""",
    validate=SAME + """
EXP="kubectl get pods -A --field-selector=status.phase!=Running,status.phase!=Succeeded -o jsonpath='{range .items[*]}{.metadata.namespace}/{.metadata.name}{\\"\\\\n\\"}{end}' | grep -v '^kube-system/'"
check "broken.txt names drill-109/badimage" file_contains "$CQ_WORK/109/broken.txt" "^drill-109/badimage$"
check "broken.txt names drill-109b/toobig" file_contains "$CQ_WORK/109/broken.txt" "^drill-109b/toobig$"
check 2 "broken.txt has exactly the not-running pods" same_sorted "$CQ_WORK/109/broken.txt" "$EXP\"""",
    solve="""kubectl get pods -A --field-selector=status.phase!=Running,status.phase!=Succeeded -o jsonpath='{range .items[*]}{.metadata.namespace}/{.metadata.name}{"\\n"}{end}' | grep -v '^kube-system/' > "$CQ_WORK/109/broken.txt\"""",
    cleanup="kubectl delete ns drill-109b --ignore-not-found --wait=false >/dev/null 2>&1",
    hints=["`--field-selector=status.phase!=Running` works on pods.", "Combine selectors with a comma. They are ANDed.", "`-A` for all namespaces, then JSONPath for `namespace/name`."],
    solution="""```bash
k get pods -A --field-selector=status.phase!=Running,status.phase!=Succeeded \\
  -o jsonpath='{range .items[*]}{.metadata.namespace}/{.metadata.name}{"\\n"}{end}' \\
  | grep -v '^kube-system/' > ~/ckaquest-work/109/broken.txt
```""",
    debrief="""# Drill: What Is Not Running

## Pattern
Field selectors filter on the server. Pods support `status.phase`, `spec.nodeName`, `metadata.name`, `metadata.namespace` and a few more.

A pod in ImagePullBackOff has phase Pending. STATUS in `k get pods` is not the phase. It is a summary.

Bookmark: https://kubernetes.io/docs/concepts/overview/working-with-objects/field-selectors/

Your notes: kubectl Cheat Sheet, Application Failure""")

level(W, "level-110-api-resources", dict(
    name="Drill: Know Your Resources",
    description="Short names, groups and scope from the API itself",
    objective="Answer API questions with api-resources and explain",
    xp=150, difficulty="beginner", expected_time="3m", domain="architecture", course_section=2,
    namespace="drills", concepts=["kubectl api-resources", "kubectl explain", "API groups"],
    task="""Write to `~/ckaquest-work/110/answers.txt` exactly three lines:
1. the short name of **poddisruptionbudgets**
2. the API group of **ingressclasses**
3. `true` or `false`: is **persistentvolumes** namespaced?

Par time: 3 minutes.""",
    docs=["https://kubernetes.io/docs/reference/kubectl/generated/kubectl_api-resources/"]),
    setup=reset(110),
    validate="""check 3 "answers are pdb, networking.k8s.io, false" out_eq "$(printf 'pdb\\nnetworking.k8s.io\\nfalse')" sh -c "sed -e 's/[[:space:]]*$//' -e '/^$/d' '$CQ_WORK/110/answers.txt'\"""",
    solve="""printf 'pdb\\nnetworking.k8s.io\\nfalse\\n' > "$CQ_WORK/110/answers.txt\"""",
    hints=["`k api-resources` has the columns SHORTNAMES, APIVERSION, NAMESPACED.", "The group is the part of APIVERSION before the slash.", "`k api-resources | grep -E 'poddisruption|ingressclass|persistentvolumes'`"],
    solution="""```bash
k api-resources | grep -E 'poddisruptionbudgets|ingressclasses|^persistentvolumes'
printf 'pdb\\nnetworking.k8s.io\\nfalse\\n' > ~/ckaquest-work/110/answers.txt
```""",
    debrief="""# Drill: Know Your Resources

## Pattern
`k api-resources` answers most "what is the name/group/scope" questions. `--namespaced=false` lists cluster-scoped kinds. `k explain <kind>` shows the version and fields.

Bookmark: https://kubernetes.io/docs/reference/kubectl/generated/kubectl_api-resources/

Your notes: API Groups, kubectl Cheat Sheet""")
