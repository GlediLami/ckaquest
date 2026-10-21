"""Writes World 9 (Helm, Kustomize, CRDs and operators)."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
from genlib import level

W = "world-9-packaging"
REPO = '"$CQ_ROOT/bin/cq-helm-repo" ensure >/dev/null'
HELM_DOCS = "https://helm.sh/docs/helm/helm_install/"
KUST_DOCS = "https://kubernetes.io/docs/tasks/manage-kubernetes-objects/kustomization/"


def fresh_releases(ns):
    return f'for r in $(helm list -n {ns} -aq 2>/dev/null); do helm uninstall "$r" -n {ns} >/dev/null 2>&1; done'


level(W, "level-79-helm-install", dict(
    name="Install From a Repo",
    description="Install the webapp chart from the team's chart repository",
    objective="Add a Helm repo and install a pinned chart version with custom values",
    xp=200, difficulty="beginner", expected_time="6m", domain="architecture", course_section=12,
    namespace="helm-shop", concepts=["helm repo add", "helm install", "--version", "--set"],
    task="""The team's chart repository is at `http://127.0.0.1:8879`.

1. Add it as repo **cq**.
2. Install chart **cq/webapp** version **1.0.0** as release **shop** in namespace **helm-shop**, with **2** replicas.""",
    docs=[HELM_DOCS, "https://helm.sh/docs/helm/helm_repo_add/"]),
    setup=REPO + "\n" + fresh_releases("helm-shop") + "\nhelm repo remove cq >/dev/null 2>&1 || true",
    validate="""chart() { helm list -n helm-shop -o json | python3 -c 'import json,sys; print(" ".join(r["chart"] + ":" + r["status"] for r in json.load(sys.stdin) if r["name"] == "shop"))'; }
check "repo cq points at http://127.0.0.1:8879" out_match "^cq[[:space:]]+http://127.0.0.1:8879" helm repo list
check 2 "release shop runs chart webapp-1.0.0" out_eq "webapp-1.0.0:deployed" chart
check 2 "shop-webapp has 2/2 ready replicas" deploy_ready helm-shop shop-webapp 2""",
    solve="""helm repo add cq http://127.0.0.1:8879
helm repo update cq
helm install shop cq/webapp --version 1.0.0 -n helm-shop --set replicaCount=2 --wait""",
    cleanup=fresh_releases("helm-shop"),
    hints=["`helm repo add <name> <url>`, then `helm search repo cq --versions`.",
           "`helm show values cq/webapp` lists what you can set. The replica count is a top-level value.",
           "`helm install shop cq/webapp --version 1.0.0 -n helm-shop --set replicaCount=2`"],
    solution="""```bash
helm repo add cq http://127.0.0.1:8879
helm search repo cq/webapp --versions
helm show values cq/webapp --version 1.0.0
helm install shop cq/webapp --version 1.0.0 -n helm-shop --set replicaCount=2
helm list -n helm-shop
```""",
    debrief="""# Install From a Repo

## What happened
A chart is a package of templates. A release is one installation of a chart in a namespace. Values fill the templates.

## Commands to know
- `helm repo add / update / list`
- `helm search repo <name> --versions`
- `helm show values <chart>` before you install
- `helm install <release> <chart> --version X -n <ns> [--create-namespace] --set k=v | -f values.yaml`
- `helm list -A` shows releases in all namespaces

## Exam angle
- Helm commands need `-n`. A release in the wrong namespace is a lost task.
- Pin `--version` when the task names one.

Bookmark: https://helm.sh/docs/helm/helm_install/

Your notes: Helm (course section 12)""")

level(W, "level-80-helm-rollback", dict(
    name="Bad Upgrade",
    description="An upgrade broke the release",
    objective="Roll the Helm release back to the last working revision",
    xp=250, difficulty="intermediate", expected_time="6m", domain="architecture", course_section=12,
    namespace="helm-blog", concepts=["helm history", "helm rollback", "revisions"],
    task="""Release **blog** in namespace **helm-blog** was upgraded and its pods no longer start.

Roll it back to the last revision that worked. Use Helm, not kubectl.""",
    docs=["https://helm.sh/docs/helm/helm_rollback/", "https://helm.sh/docs/helm/helm_history/"]),
    setup=REPO + "\n" + fresh_releases("helm-blog") + """
helm install blog webapp --repo http://127.0.0.1:8879 --version 1.0.0 -n helm-blog --wait >/dev/null
helm upgrade blog webapp --repo http://127.0.0.1:8879 --version 1.1.0 -n helm-blog --set replicaCount=2 >/dev/null
helm upgrade blog webapp --repo http://127.0.0.1:8879 --version 1.1.0 -n helm-blog --reuse-values --set image.tag=1.28-alpine-broken >/dev/null""",
    validate="""last() { helm history blog -n helm-blog -o json | python3 -c 'import json,sys; h=json.load(sys.stdin)[-1]; print(h["status"], h["description"])'; }
check 2 "the latest revision is a rollback to revision 2" out_match "deployed Rollback to 2" last
check "blog runs the 1.28-alpine image" field_eq helm-blog deploy/blog-webapp '{.spec.template.spec.containers[0].image}' nginx:1.28-alpine
check 2 "blog-webapp has 2/2 ready replicas" deploy_ready helm-blog blog-webapp 2""",
    solve="helm rollback blog 2 -n helm-blog --wait",
    cleanup=fresh_releases("helm-blog"),
    hints=["`helm history blog -n helm-blog`. Which revisions are there and what changed?",
           "Revision 3 set a broken image tag. Revision 2 was the last good one, not revision 1.",
           "`helm rollback blog 2 -n helm-blog`"],
    solution="""```bash
helm history blog -n helm-blog
helm get values blog -n helm-blog --revision 3      # image.tag: 1.28-alpine-broken
helm rollback blog 2 -n helm-blog
k get pods -n helm-blog
```""",
    debrief="""# Bad Upgrade

## What happened
Every install, upgrade and rollback is a numbered revision, stored as a Secret in the release namespace. A rollback creates a new revision that copies an old one.

## Commands to know
- `helm history <release>`
- `helm get values <release> --revision N` and `helm get manifest`
- `helm rollback <release> <revision>`. Without a revision it goes back one step.

## Exam angle
- "Roll back to the last working version" needs history first. The last working one is not always revision 1.
- `kubectl rollout undo` on the Deployment would fight Helm. Use Helm for Helm releases.

Bookmark: https://helm.sh/docs/helm/helm_rollback/

Your notes: Helm (course section 12)""")

level(W, "level-81-helm-find", dict(
    name="Find the Old Release",
    description="Security wants every release that still runs nginx 1.27 gone",
    objective="Find releases across namespaces and uninstall the right ones",
    xp=250, difficulty="intermediate", expected_time="8m", domain="architecture", course_section=12,
    namespace="helm-audit", concepts=["helm list -A", "helm uninstall", "chart versions"],
    task="""Several Helm releases run in namespaces **helm-audit**, **helm-team-a** and **helm-team-b**.

Uninstall every release that uses chart **webapp-1.0.0**. Keep all other releases.""",
    docs=["https://helm.sh/docs/helm/helm_list/", "https://helm.sh/docs/helm/helm_uninstall/"]),
    setup=REPO + """
for ns in helm-audit helm-team-a helm-team-b; do kubectl create ns $ns --dry-run=client -o yaml | kubectl apply -f - >/dev/null; done
""" + "\n".join(fresh_releases(n) for n in ("helm-audit", "helm-team-a", "helm-team-b")) + """
helm install old-api webapp --repo http://127.0.0.1:8879 --version 1.0.0 -n helm-team-a >/dev/null
helm install new-api webapp --repo http://127.0.0.1:8879 --version 1.1.0 -n helm-team-a >/dev/null
helm install old-web webapp --repo http://127.0.0.1:8879 --version 1.0.0 -n helm-team-b >/dev/null
helm install portal webapp --repo http://127.0.0.1:8879 --version 1.1.0 -n helm-audit >/dev/null""",
    validate="""rel() { helm status "$1" -n "$2" >/dev/null 2>&1; }
norel() { ! rel "$@"; }
check 2 "old-api (webapp-1.0.0) is gone" norel old-api helm-team-a
check 2 "old-web (webapp-1.0.0) is gone" norel old-web helm-team-b
check "new-api is still installed" rel new-api helm-team-a
check "portal is still installed" rel portal helm-audit""",
    solve="""helm uninstall old-api -n helm-team-a
helm uninstall old-web -n helm-team-b""",
    cleanup="\n".join(fresh_releases(n) for n in ("helm-audit", "helm-team-a", "helm-team-b")) + "\nkubectl delete ns helm-team-a helm-team-b --ignore-not-found --wait=false >/dev/null 2>&1",
    hints=["`helm list` only shows one namespace. Add `-A`.", "The CHART column shows name and version.", "`helm uninstall <release> -n <ns>` for each one with webapp-1.0.0."],
    solution="""```bash
helm list -A
helm list -A | grep webapp-1.0.0
helm uninstall old-api -n helm-team-a
helm uninstall old-web -n helm-team-b
```""",
    debrief="""# Find the Old Release

## What happened
Releases live in namespaces. `helm list -A` is the only quick overview. Filter with grep or `--filter <regex>` on the release name.

## Exam angle
- "Delete all releases of chart X" or "the release in pending-install state" are common. `helm list -A -a` also shows failed and pending ones.
- `helm uninstall` needs the right `-n`.

Bookmark: https://helm.sh/docs/helm/helm_list/

Your notes: Helm (course section 12)""")

level(W, "level-82-helm-template", dict(
    name="Render, Don't Install",
    description="Review a chart's output before it touches the cluster",
    objective="Render a chart to a file with helm template",
    xp=200, difficulty="intermediate", expected_time="5m", domain="architecture", course_section=12,
    namespace="helm-render", concepts=["helm template", "values", "dry run"],
    task="""Render chart **webapp** version **1.1.0** from `http://127.0.0.1:8879` as release **preview** with **3** replicas and service type **NodePort**.

Write the rendered manifests to `~/ckaquest-work/82/preview.yaml`. Do not install anything.""",
    docs=["https://helm.sh/docs/helm/helm_template/"]),
    setup=REPO + "\n" + fresh_releases("helm-render") + '\nW="$(cq_work_dir 82)"; mv -f "$W/preview.yaml" "$W/preview.yaml.old" 2>/dev/null || true',
    validate="""F="$CQ_WORK/82/preview.yaml"
check "preview.yaml exists" file_exists "$F"
check 2 "it has replicas: 3" file_contains "$F" "replicas: 3"
check 2 "it has type: NodePort" file_contains "$F" "type: NodePort"
check "it is release preview with nginx:1.28-alpine" file_contains "$F" "preview-webapp"
check "nothing was installed" out_eq "" helm list -n helm-render -q""",
    solve='helm template preview webapp --repo http://127.0.0.1:8879 --version 1.1.0 --set replicaCount=3 --set service.type=NodePort > "$CQ_WORK/82/preview.yaml"',
    cleanup=fresh_releases("helm-render"),
    hints=["`helm template` renders locally. It takes the same chart and value flags as install.", "Value names: `helm show values webapp --repo http://127.0.0.1:8879`.", "Redirect stdout to the file."],
    solution="""```bash
helm template preview webapp --repo http://127.0.0.1:8879 --version 1.1.0 \\
  --set replicaCount=3 --set service.type=NodePort > ~/ckaquest-work/82/preview.yaml
```""",
    debrief="""# Render, Don't Install

## What happened
`helm template` runs the templates locally and prints YAML. Nothing reaches the cluster, no release is stored.

## Related
- `helm install --dry-run=client` does nearly the same but goes through the install path.
- `helm get manifest <release>` shows what an installed release rendered.

## Exam angle
- Useful to answer "what image would this chart deploy" without installing.

Bookmark: https://helm.sh/docs/helm/helm_template/

Your notes: Helm (course section 12)""")

KBASE = """W="$(cq_work_dir 83)"
mkdir -p "$W/base"
cat > "$W/base/deployment.yaml" <<'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
spec:
  replicas: 1
  selector:
    matchLabels: {app: web}
  template:
    metadata:
      labels: {app: web}
    spec:
      containers:
      - name: web
        image: nginx:1.27-alpine
        ports:
        - containerPort: 80
EOF
cat > "$W/base/service.yaml" <<'EOF'
apiVersion: v1
kind: Service
metadata:
  name: web
spec:
  selector: {app: web}
  ports:
  - port: 80
EOF
cat > "$W/base/kustomization.yaml" <<'EOF'
resources:
- deployment.yaml
- service.yaml
EOF"""

level(W, "level-83-kustomize-overlay", dict(
    name="A Production Overlay",
    description="The same app needs a production variant",
    objective="Write a Kustomize overlay and apply it",
    xp=300, difficulty="intermediate", expected_time="10m", domain="architecture", course_section=13,
    namespace="kustomize-prod", concepts=["kustomization.yaml", "overlays", "namePrefix", "images", "replicas"],
    task="""`~/ckaquest-work/83/base/` holds a Kustomize base (Deployment and Service **web**).

Create an overlay in `~/ckaquest-work/83/overlays/prod/` that:
- uses the base
- sets namespace **kustomize-prod**
- adds the name prefix **prod-**
- sets **3** replicas for the Deployment
- changes the nginx image tag to **1.28-alpine**

Apply the overlay with kubectl. Do not edit the base.""",
    docs=[KUST_DOCS]),
    setup=KBASE.replace("83", "83") + '\nmv -f "$W/overlays" "$W/overlays.old.$(date +%s)" 2>/dev/null || true',
    validate="""check "base is unchanged (replicas 1)" file_contains "$CQ_WORK/83/base/deployment.yaml" "replicas: 1"
check "overlay kustomization exists" file_exists "$CQ_WORK/83/overlays/prod/kustomization.yaml"
check 2 "Deployment prod-web runs 3 ready replicas" deploy_ready kustomize-prod prod-web 3
check 2 "prod-web uses nginx:1.28-alpine" field_eq kustomize-prod deploy/prod-web '{.spec.template.spec.containers[0].image}' nginx:1.28-alpine
check "Service prod-web exists" exists kustomize-prod svc/prod-web""",
    solve="""mkdir -p "$CQ_WORK/83/overlays/prod"
cat > "$CQ_WORK/83/overlays/prod/kustomization.yaml" <<'EOF'
resources:
- ../../base
namespace: kustomize-prod
namePrefix: prod-
replicas:
- name: web
  count: 3
images:
- name: nginx
  newTag: 1.28-alpine
EOF
kubectl apply -k "$CQ_WORK/83/overlays/prod"
kubectl rollout status deploy/prod-web -n kustomize-prod --timeout=120s""",
    hints=["An overlay is a folder with its own kustomization.yaml that lists the base under `resources: - ../../base`.",
           "Kustomize has fields for each change: `namespace`, `namePrefix`, `replicas`, `images`. No patches needed.",
           "Check the output first with `k kustomize overlays/prod`, then `k apply -k overlays/prod`."],
    solution="""```yaml
# ~/ckaquest-work/83/overlays/prod/kustomization.yaml
resources:
- ../../base
namespace: kustomize-prod
namePrefix: prod-
replicas:
- name: web
  count: 3
images:
- name: nginx
  newTag: 1.28-alpine
```

```bash
k kustomize ~/ckaquest-work/83/overlays/prod
k apply -k ~/ckaquest-work/83/overlays/prod
```""",
    debrief="""# A Production Overlay

## What happened
Kustomize builds YAML from a base plus overlays, without templates. Common changes have their own fields. Everything else is a patch (next level).

## Commands
- `kubectl kustomize <dir>` prints the result.
- `kubectl apply -k <dir>` applies it. `kubectl delete -k <dir>` removes it.

## Exam angle
- Know the built-in fields: `namespace`, `namePrefix`, `nameSuffix`, `labels` (or `commonLabels`), `images`, `replicas`, `configMapGenerator`, `patches`.
- `-k` takes a folder, not a file.

Bookmark: https://kubernetes.io/docs/tasks/manage-kubernetes-objects/kustomization/

Your notes: Kustomize (course section 13)""")

level(W, "level-84-kustomize-patch", dict(
    name="Patch It In",
    description="Production needs limits and a config that the base does not have",
    objective="Use a patch and a configMapGenerator in an overlay",
    xp=300, difficulty="advanced", expected_time="10m", domain="architecture", course_section=13,
    namespace="kustomize-patch", concepts=["patches", "strategic merge", "configMapGenerator"],
    task="""Use the base in `~/ckaquest-work/84/base/`. Create the overlay `~/ckaquest-work/84/overlays/prod/` that:
- sets namespace **kustomize-patch**
- adds memory limit **128Mi** and CPU limit **200m** to container **web** with a patch
- generates a ConfigMap **web-config** with `MODE=production`, and the Deployment loads it with `envFrom`

Apply it with kubectl. Do not edit the base.""",
    docs=[KUST_DOCS, "https://kubectl.docs.kubernetes.io/references/kustomize/kustomization/patches/"]),
    setup=KBASE.replace("cq_work_dir 83", "cq_work_dir 84") + '\nmv -f "$W/overlays" "$W/overlays.old.$(date +%s)" 2>/dev/null || true',
    validate="""C="{.spec.template.spec.containers[0]"
cm_name() { jp kustomize-patch deploy/web "$C.envFrom[0].configMapRef.name}"; }
cm_ok() { local n; n="$(cm_name)"; [ -n "$n" ] && field_eq kustomize-patch "cm/$n" '{.data.MODE}' production; }
check 2 "web has memory limit 128Mi" field_eq kustomize-patch deploy/web "$C.resources.limits.memory}" 128Mi
check "web has CPU limit 200m" field_eq kustomize-patch deploy/web "$C.resources.limits.cpu}" 200m
check 2 "web loads a generated web-config with MODE=production" cm_ok
check "the ConfigMap name has the generator hash" out_match "^web-config-[a-z0-9]+$" cm_name
check "web is ready" deploy_ready kustomize-patch web
check "base is unchanged" sh -c '! grep -q limits "$CQ_WORK/84/base/deployment.yaml"'""",
    solve="""O="$CQ_WORK/84/overlays/prod"
mkdir -p "$O"
cat > "$O/limits.yaml" <<'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
spec:
  template:
    spec:
      containers:
      - name: web
        resources:
          limits:
            memory: 128Mi
            cpu: 200m
        envFrom:
        - configMapRef:
            name: web-config
EOF
cat > "$O/kustomization.yaml" <<'EOF'
resources:
- ../../base
namespace: kustomize-patch
patches:
- path: limits.yaml
configMapGenerator:
- name: web-config
  literals:
  - MODE=production
EOF
kubectl apply -k "$O"
kubectl rollout status deploy/web -n kustomize-patch --timeout=120s""",
    hints=["A strategic merge patch is a partial Deployment: name, then only the path down to what you change. List it under `patches: - path: file.yaml`.",
           "`configMapGenerator` creates a ConfigMap with a hash suffix. Kustomize rewrites references to it in the same build.",
           "Put `envFrom: - configMapRef: name: web-config` in the patch next to the limits. Kustomize adds the hash."],
    solution="""```yaml
# overlays/prod/kustomization.yaml
resources:
- ../../base
namespace: kustomize-patch
patches:
- path: limits.yaml
configMapGenerator:
- name: web-config
  literals:
  - MODE=production
```

```yaml
# overlays/prod/limits.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
spec:
  template:
    spec:
      containers:
      - name: web
        resources:
          limits: {memory: 128Mi, cpu: 200m}
        envFrom:
        - configMapRef: {name: web-config}
```""",
    debrief="""# Patch It In

## What happened
Strategic merge patches merge lists by key. Containers merge by `name`, so the patch only needs `name: web` and the new fields.

`configMapGenerator` adds a content hash to the name. When the data changes, the name changes and the Deployment rolls out. That is the main reason to use it.

## Patch types
- Strategic merge (a partial object) for most changes.
- JSON 6902 (`op: replace, path: /spec/...`) for exact edits, also on CRDs.
- Both go under `patches:`. `patchesStrategicMerge` is the old field name.

## Exam angle
- Build first with `k kustomize`, read it, then apply.

Bookmark: https://kubernetes.io/docs/tasks/manage-kubernetes-objects/kustomization/

Your notes: Kustomize (course section 13)""")

CRD = """apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: backups.ops.example.com
spec:
  group: ops.example.com
  scope: Namespaced
  names:
    plural: backups
    singular: backup
    kind: Backup
    shortNames: [bk]
  versions:
  - name: v1
    served: true
    storage: true
    schema:
      openAPIV3Schema:
        type: object
        properties:
          spec:
            type: object
            required: [schedule, target]
            properties:
              schedule: {type: string}
              target: {type: string}
              retain: {type: integer, minimum: 1}"""

level(W, "level-85-crd", dict(
    name="Your Own Resource Type",
    description="The ops team ships a Backup resource",
    objective="Install a CRD and create a custom resource that passes its schema",
    xp=250, difficulty="intermediate", expected_time="8m", domain="architecture", course_section=9,
    namespace="crd-lab", concepts=["CustomResourceDefinition", "custom resources", "kubectl explain", "schema validation"],
    task="""The CRD for **backups.ops.example.com** is in `~/ckaquest-work/85/backup-crd.yaml`.

1. Install it.
2. In namespace **crd-lab**, create a Backup **nightly** with schedule `0 2 * * *`, target `postgres` and retain `7`.
3. Write the short name of the Backup resource to `~/ckaquest-work/85/shortname.txt`.""",
    docs=["https://kubernetes.io/docs/tasks/extend-kubernetes/custom-resources/custom-resource-definitions/"]),
    setup=f"""W="$(cq_work_dir 85)"
cat > "$W/backup-crd.yaml" <<'EOF'
{CRD}
EOF
mv -f "$W/shortname.txt" "$W/shortname.txt.old" 2>/dev/null || true
kubectl delete crd backups.ops.example.com --ignore-not-found --timeout=60s >/dev/null""",
    validate="""check "CRD backups.ops.example.com is Established" field_eq - crd/backups.ops.example.com '{.status.conditions[?(@.type=="Established")].status}' True
check 2 "Backup nightly has the right spec" out_eq "0 2 * * *|postgres|7" kubectl get backup nightly -n crd-lab -o jsonpath='{.spec.schedule}|{.spec.target}|{.spec.retain}'
check "shortname.txt says bk" file_eq "$CQ_WORK/85/shortname.txt" bk""",
    solve="""kubectl apply -f "$CQ_WORK/85/backup-crd.yaml"
kubectl wait --for=condition=Established crd/backups.ops.example.com --timeout=30s
cat <<'EOF' | kubectl apply -f -
apiVersion: ops.example.com/v1
kind: Backup
metadata:
  name: nightly
  namespace: crd-lab
spec:
  schedule: "0 2 * * *"
  target: postgres
  retain: 7
EOF
echo bk > "$CQ_WORK/85/shortname.txt\"""",
    cleanup="kubectl delete crd backups.ops.example.com --ignore-not-found --wait=false >/dev/null 2>&1",
    hints=["`k apply -f backup-crd.yaml`, then `k api-resources | grep backup`.", "`k explain backup.spec` shows the fields once the CRD is installed.", "apiVersion of the object is `<group>/<version>`: ops.example.com/v1, kind Backup. Quote the schedule string."],
    solution="""```bash
k apply -f ~/ckaquest-work/85/backup-crd.yaml
k api-resources | grep backups          # SHORTNAMES column: bk
k explain backup.spec
cat <<EOF | k apply -f -
apiVersion: ops.example.com/v1
kind: Backup
metadata:
  name: nightly
  namespace: crd-lab
spec:
  schedule: "0 2 * * *"
  target: postgres
  retain: 7
EOF
echo bk > ~/ckaquest-work/85/shortname.txt
```""",
    debrief="""# Your Own Resource Type

## What happened
A CRD teaches the API server a new resource. After that, kubectl works with it like any built-in type: get, describe, explain, RBAC. The openAPIV3Schema validates what you store.

## Exam angle
- `k get crd`, `k api-resources --api-group=<group>`, `k explain <kind>.spec` are your tools.
- A CRD alone does nothing. A controller (operator) watches the objects and acts. Next level.
- A cron string with `*` must be quoted in YAML.

Bookmark: https://kubernetes.io/docs/tasks/extend-kubernetes/custom-resources/custom-resource-definitions/

Your notes: Custom Resources and Operators""")

level(W, "level-86-operator-rbac", dict(
    name="The Operator Cannot See",
    description="A backup operator logs Forbidden for its own custom resources",
    objective="Give an operator RBAC on a custom resource group",
    xp=300, difficulty="advanced", expected_time="8m", domain="architecture", course_section=9,
    namespace="backup-system", concepts=["ClusterRole", "custom resources", "apiGroups", "operators"],
    task="""Deployment **backup-operator** in namespace **backup-system** runs as ServiceAccount **backup-operator** and must watch Backup objects (`backups.ops.example.com`) in **all** namespaces. It also updates their status.

It logs `Forbidden`. Create ClusterRole **backup-operator** and ClusterRoleBinding **backup-operator** that grant `get`, `list`, `watch`, `update` and `patch` on `backups` and `backups/status` in API group `ops.example.com`. Nothing else.""",
    docs=["https://kubernetes.io/docs/reference/access-authn-authz/rbac/#referring-to-resources"]),
    setup=f"""cat <<'EOF' | kubectl apply -f - >/dev/null
{CRD}
EOF
kubectl delete clusterrole backup-operator --ignore-not-found >/dev/null
kubectl delete clusterrolebinding backup-operator --ignore-not-found >/dev/null
kubectl create serviceaccount backup-operator -n backup-system >/dev/null
cat <<'EOF' | kubectl apply -f - >/dev/null
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backup-operator
  namespace: backup-system
spec:
  replicas: 1
  selector:
    matchLabels: {{app: backup-operator}}
  template:
    metadata:
      labels: {{app: backup-operator}}
    spec:
      serviceAccountName: backup-operator
      containers:
      - name: operator
        image: bitnami/kubectl:latest
        imagePullPolicy: IfNotPresent
        command: ["sh", "-c", "while true; do kubectl get backups.ops.example.com -A 2>&1 | tail -1; sleep 5; done"]
EOF""",
    validate="""SA=system:serviceaccount:backup-system:backup-operator
works() { ! kubectl logs deploy/backup-operator -n backup-system --tail=1 2>/dev/null | grep -qi forbidden; }
check 2 "operator can list backups in all namespaces" can_i "$SA" list backups.ops.example.com
check "operator can watch backups" can_i "$SA" watch backups.ops.example.com
status_ok() { [ "$(kubectl auth can-i patch backups.ops.example.com --subresource=status --as="$SA" -A 2>/dev/null)" = yes ]; }
check "operator can patch backups/status" status_ok
check "operator cannot delete backups" cannot_i "$SA" delete backups.ops.example.com
check "operator cannot list pods" cannot_i "$SA" list pods
check 2 "operator log shows no Forbidden" works""",
    solve="""cat <<'EOF' | kubectl apply -f -
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: backup-operator
rules:
- apiGroups: ["ops.example.com"]
  resources: ["backups", "backups/status"]
  verbs: ["get", "list", "watch", "update", "patch"]
EOF
kubectl create clusterrolebinding backup-operator --clusterrole=backup-operator --serviceaccount=backup-system:backup-operator
sleep 12""",
    cleanup="""kubectl delete clusterrolebinding backup-operator --ignore-not-found >/dev/null 2>&1
kubectl delete clusterrole backup-operator --ignore-not-found >/dev/null 2>&1
kubectl delete crd backups.ops.example.com --ignore-not-found --wait=false >/dev/null 2>&1""",
    hints=["The RBAC rule needs the API group of the CRD, not \"\". `k get crd backups.ops.example.com -o jsonpath='{.spec.group}'`.",
           "Subresources like status are written as `backups/status` in `resources`.",
           "`k create clusterrole backup-operator --verb=get,list,watch,update,patch --resource=backups.ops.example.com,backups.ops.example.com/status` also works."],
    solution="""```bash
k create clusterrole backup-operator --verb=get,list,watch,update,patch \\
  --resource=backups.ops.example.com,backups.ops.example.com/status
k create clusterrolebinding backup-operator --clusterrole=backup-operator \\
  --serviceaccount=backup-system:backup-operator
k auth can-i list backups.ops.example.com -A --as=system:serviceaccount:backup-system:backup-operator
```""",
    debrief="""# The Operator Cannot See

## What happened
RBAC rules match on API group plus resource. Core resources have group `""`. Custom resources have the CRD's group. A rule with the wrong group grants nothing, without any error.

## Facts to remember
- `--resource=<plural>.<group>` in `kubectl create clusterrole` sets the group for you.
- Subresources (`status`, `scale`, `log`, `exec`) need their own entry.
- An operator that watches all namespaces needs a ClusterRoleBinding.

## Exam angle
- Operators and CRDs are in the curriculum. Expect to install one from a manifest and fix its RBAC.

Bookmark: https://kubernetes.io/docs/reference/access-authn-authz/rbac/

Your notes: Custom Resources and Operators, Cluster Roles""")
