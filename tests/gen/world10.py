"""Writes World 10 (workloads, autoscaling, storage)."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
from genlib import level

W = "world-10-workloads-2"

level(W, "level-87-native-sidecar", dict(
    name="A Sidecar That Starts First",
    description="The log shipper must run for the whole life of the pod",
    objective="Add a native sidecar container",
    xp=300, difficulty="intermediate", expected_time="8m", domain="workloads", course_section=5,
    namespace="sidecar-lab", concepts=["native sidecar", "initContainers restartPolicy Always", "emptyDir"],
    task="""Pod **app** in namespace **sidecar-lab** writes logs to `/var/log/app/app.log` on an emptyDir volume **logs**.

Recreate the pod with a **native sidecar** container **log-shipper** (image `busybox:1.36`) that runs `tail -F /var/log/app/app.log` and mounts the same volume. It must start before the app container and keep running.""",
    docs=["https://kubernetes.io/docs/concepts/workloads/pods/sidecar-containers/"]),
    setup="""cat <<'EOF' | kubectl apply -f - >/dev/null
apiVersion: v1
kind: Pod
metadata:
  name: app
  namespace: sidecar-lab
spec:
  containers:
  - name: app
    image: busybox:1.36
    command: ["sh", "-c", "mkdir -p /var/log/app; while true; do echo \\"$(date) order processed\\" >> /var/log/app/app.log; sleep 2; done"]
    volumeMounts:
    - name: logs
      mountPath: /var/log/app
  volumes:
  - name: logs
    emptyDir: {}
EOF""",
    validate="""I='{.spec.initContainers[?(@.name=="log-shipper")]'
ships() { kubectl logs app -n sidecar-lab -c log-shipper --tail=3 2>/dev/null | grep -q "order processed"; }
check 2 "log-shipper is an init container with restartPolicy Always" field_eq sidecar-lab pod/app "$I.restartPolicy}" Always
check "it mounts the logs volume" field_eq sidecar-lab pod/app "$I.volumeMounts[0].name}" logs
check "pod app is Ready" pod_ready sidecar-lab app
check 2 "log-shipper prints the app log" ships""",
    solve="""kubectl delete pod app -n sidecar-lab --now
cat <<'EOF' | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: app
  namespace: sidecar-lab
spec:
  initContainers:
  - name: log-shipper
    image: busybox:1.36
    restartPolicy: Always
    command: ["sh", "-c", "touch /var/log/app/app.log; tail -F /var/log/app/app.log"]
    volumeMounts:
    - name: logs
      mountPath: /var/log/app
  containers:
  - name: app
    image: busybox:1.36
    command: ["sh", "-c", "mkdir -p /var/log/app; while true; do echo \\"$(date) order processed\\" >> /var/log/app/app.log; sleep 2; done"]
    volumeMounts:
    - name: logs
      mountPath: /var/log/app
  volumes:
  - name: logs
    emptyDir: {}
EOF
kubectl wait --for=condition=Ready pod/app -n sidecar-lab --timeout=90s; sleep 6""",
    hints=["A native sidecar is an entry under `initContainers` with `restartPolicy: Always`.",
           "Containers in a pod cannot be added in place. Export the pod, edit, `k replace --force -f`.",
           "Mount volume `logs` at /var/log/app in the sidecar too. Check with `k logs app -c log-shipper`."],
    solution="""```yaml
spec:
  initContainers:
  - name: log-shipper
    image: busybox:1.36
    restartPolicy: Always
    command: ["sh", "-c", "tail -F /var/log/app/app.log"]
    volumeMounts:
    - name: logs
      mountPath: /var/log/app
```

```bash
k get pod app -n sidecar-lab -o yaml > app.yaml   # add the block above
k replace --force -f app.yaml
k logs app -n sidecar-lab -c log-shipper
```""",
    debrief="""# A Sidecar That Starts First

## What happened
Since Kubernetes 1.29 (GA in 1.33), an init container with `restartPolicy: Always` is a sidecar. It starts before the app containers, keeps running, is restarted if it dies, and stops after them. Jobs finish even though the sidecar never exits.

## Old way versus native
- A plain second container has no start order and keeps Jobs from completing.
- A native sidecar has a start order, has probes, and lets Jobs end.

## Exam angle
- "Add a sidecar" in a current exam means this pattern.
- `k logs <pod> -c <container>` for each container.

Bookmark: https://kubernetes.io/docs/concepts/workloads/pods/sidecar-containers/

Your notes: Multi-Container Pods""")

level(W, "level-88-three-containers", dict(
    name="Three in One",
    description="Build a pod with three containers that share a volume",
    objective="Write a multi-container pod from scratch",
    xp=250, difficulty="intermediate", expected_time="8m", domain="workloads", course_section=5,
    namespace="trio-lab", concepts=["multi-container pods", "shared volumes", "env from fieldRef"],
    task="""Create pod **trio** in namespace **trio-lab** with an emptyDir volume **shared** and three containers:
- **writer**: `busybox:1.36`, runs `while true; do date >> /data/dates; sleep 5; done`, mounts shared at `/data`
- **reader**: `busybox:1.36`, runs `tail -F /data/dates`, mounts shared at `/data`
- **info**: `busybox:1.36`, has env var `MY_NODE` set to the node name (from the pod spec), runs `sleep 3600`""",
    docs=["https://kubernetes.io/docs/tasks/access-application-cluster/communicate-containers-same-pod-shared-volume/",
          "https://kubernetes.io/docs/tasks/inject-data-application/environment-variable-expose-pod-information/"]),
    validate="""ready3() { [ "$(jp trio-lab pod/trio '{.status.containerStatuses[*].ready}')" = "true true true" ]; }
node_env() { [ "$(kubectl exec trio -n trio-lab -c info -- printenv MY_NODE 2>/dev/null)" = "$(jp trio-lab pod/trio '{.spec.nodeName}')" ]; }
check "trio has containers writer, reader, info" out_eq "writer reader info" kubectl get pod trio -n trio-lab -o jsonpath='{.spec.containers[*].name}'
check 2 "all 3 containers are ready" ready3
check 2 "reader sees what writer writes" out_match "[0-9]{2}:[0-9]{2}" kubectl logs trio -n trio-lab -c reader --tail=1
check 2 "info has MY_NODE = its node name" node_env""",
    solve="""cat <<'EOF' | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: trio
  namespace: trio-lab
spec:
  volumes:
  - name: shared
    emptyDir: {}
  containers:
  - name: writer
    image: busybox:1.36
    command: ["sh", "-c", "while true; do date >> /data/dates; sleep 5; done"]
    volumeMounts: [{name: shared, mountPath: /data}]
  - name: reader
    image: busybox:1.36
    command: ["sh", "-c", "tail -F /data/dates"]
    volumeMounts: [{name: shared, mountPath: /data}]
  - name: info
    image: busybox:1.36
    command: ["sleep", "3600"]
    env:
    - name: MY_NODE
      valueFrom:
        fieldRef: {fieldPath: spec.nodeName}
EOF
kubectl wait --for=condition=Ready pod/trio -n trio-lab --timeout=90s; sleep 6""",
    hints=["Start with `k run trio -n trio-lab --image=busybox:1.36 $do -- sh -c '...' > trio.yaml` and copy the container block twice.",
           "One `volumes:` entry, mounted by two containers.", "`valueFrom: fieldRef: fieldPath: spec.nodeName` is the Downward API."],
    solution="""```yaml
apiVersion: v1
kind: Pod
metadata:
  name: trio
  namespace: trio-lab
spec:
  volumes:
  - name: shared
    emptyDir: {}
  containers:
  - name: writer
    image: busybox:1.36
    command: ["sh", "-c", "while true; do date >> /data/dates; sleep 5; done"]
    volumeMounts: [{name: shared, mountPath: /data}]
  - name: reader
    image: busybox:1.36
    command: ["sh", "-c", "tail -F /data/dates"]
    volumeMounts: [{name: shared, mountPath: /data}]
  - name: info
    image: busybox:1.36
    command: ["sleep", "3600"]
    env:
    - name: MY_NODE
      valueFrom:
        fieldRef: {fieldPath: spec.nodeName}
```""",
    debrief="""# Three in One

## What happened
Containers in a pod share the network namespace (localhost) and can share volumes. They do not share a filesystem otherwise.

## Downward API
`fieldRef` exposes pod fields as env vars: `metadata.name`, `metadata.namespace`, `spec.nodeName`, `status.podIP`. `resourceFieldRef` exposes requests and limits.

## Exam angle
- Generate one container with `k run $do`, then copy and edit. Faster than typing three.
- Wrong indentation under `containers:` is the usual error. `k apply --dry-run=server -f` catches it.

Bookmark: https://kubernetes.io/docs/tasks/access-application-cluster/communicate-containers-same-pod-shared-volume/

Your notes: Multi-Container Pods, Environment Variables""")

API = """kubectl create deployment api -n {ns} --image=nginx:1.27-alpine --replicas=2 >/dev/null
kubectl set resources deployment api -n {ns} --requests=cpu=50m,memory=32Mi >/dev/null
kubectl rollout status deployment api -n {ns} --timeout=90s >/dev/null"""

level(W, "level-89-hpa-behavior", dict(
    name="Scale Down Slowly",
    description="The API flaps between replica counts every minute",
    objective="Create an HPA with a scale-down stabilization window",
    xp=300, difficulty="intermediate", expected_time="8m", domain="workloads", course_section=5,
    namespace="hpa-lab", concepts=["HorizontalPodAutoscaler", "autoscaling/v2", "behavior", "stabilizationWindowSeconds"],
    task="""Create an HPA **api** in namespace **hpa-lab** for Deployment **api**:
- min **2**, max **6** replicas
- target average CPU utilization **60%**
- scale down: stabilization window of **300** seconds, and remove at most **1** pod per **60** seconds""",
    docs=["https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/#configurable-scaling-behavior"]),
    setup=API.format(ns="hpa-lab"),
    validate="""H='{.spec.behavior.scaleDown'
check "min 2, max 6" out_eq "2 6" kubectl get hpa api -n hpa-lab -o jsonpath='{.spec.minReplicas} {.spec.maxReplicas}'
check "targets 60% CPU" field_eq hpa-lab hpa/api '{.spec.metrics[0].resource.target.averageUtilization}' 60
check 2 "scaleDown stabilization window is 300s" field_eq hpa-lab hpa/api "$H.stabilizationWindowSeconds}" 300
check 2 "scaleDown policy: 1 Pod per 60s" out_eq "Pods 1 60" kubectl get hpa api -n hpa-lab -o jsonpath="$H.policies[0].type} $H.policies[0].value} $H.policies[0].periodSeconds}"
check "HPA is active" field_eq hpa-lab hpa/api '{.status.conditions[?(@.type=="ScalingActive")].status}' True""",
    solve="""cat <<'EOF' | kubectl apply -f -
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api
  namespace: hpa-lab
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
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Pods
        value: 1
        periodSeconds: 60
EOF""",
    hints=["`k autoscale deploy api -n hpa-lab --min=2 --max=6 --cpu-percent=60 $do > hpa.yaml` gives the base.",
           "Add `spec.behavior.scaleDown` from the docs section 'Configurable scaling behavior'.",
           "`k explain hpa.spec.behavior.scaleDown`"],
    solution="""```bash
k autoscale deploy api -n hpa-lab --min=2 --max=6 --cpu-percent=60 $do > hpa.yaml
```

```yaml
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Pods
        value: 1
        periodSeconds: 60
```

```bash
k apply -f hpa.yaml
k describe hpa api -n hpa-lab
```""",
    debrief="""# Scale Down Slowly

## What happened
The HPA looks at the highest recommendation within the stabilization window before it scales down. A longer window stops flapping. Policies cap the speed: Pods (absolute) or Percent.

## Defaults
- scaleDown window 300s, scaleUp window 0s.
- Without policies, scale up can double the pods every 15s.

## Exam angle
- `k autoscale` creates the basic HPA. Behavior needs YAML.
- `autoscaling/v2` is the only version with behavior and multiple metrics.

Bookmark: https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/

Your notes: Horizontal Pod Autoscaler""")

level(W, "level-90-vpa", dict(
    name="Right-Size the Pods",
    description="The team wants resource recommendations without restarts",
    objective="Create a VerticalPodAutoscaler in recommendation mode",
    xp=250, difficulty="intermediate", expected_time="6m", domain="workloads", course_section=5,
    namespace="vpa-lab", concepts=["VerticalPodAutoscaler", "updateMode", "resourcePolicy"],
    task="""The VPA CRDs are installed. Create a VerticalPodAutoscaler **api-vpa** in namespace **vpa-lab** for Deployment **api**:
- update mode **Off** (recommendations only, no evictions)
- for all containers, minimum allowed CPU **25m** and memory **32Mi**, maximum CPU **500m** and memory **256Mi**""",
    docs=["https://kubernetes.io/docs/concepts/workloads/autoscaling/vertical-pod-autoscale/",
          "https://github.com/kubernetes/autoscaler/tree/master/vertical-pod-autoscaler"]),
    setup=API.format(ns="vpa-lab"),
    validate="""P='{.spec.resourcePolicy.containerPolicies[0]'
check "targets Deployment api" out_eq "Deployment api" kubectl get vpa api-vpa -n vpa-lab -o jsonpath='{.spec.targetRef.kind} {.spec.targetRef.name}'
check 2 "updateMode is Off" field_eq vpa-lab vpa/api-vpa '{.spec.updatePolicy.updateMode}' Off
check "policy applies to all containers (*)" field_eq vpa-lab vpa/api-vpa "$P.containerName}" "*"
check 2 "minAllowed 25m / 32Mi" out_eq "25m 32Mi" kubectl get vpa api-vpa -n vpa-lab -o jsonpath="$P.minAllowed.cpu} $P.minAllowed.memory}"
check 2 "maxAllowed 500m / 256Mi" out_eq "500m 256Mi" kubectl get vpa api-vpa -n vpa-lab -o jsonpath="$P.maxAllowed.cpu} $P.maxAllowed.memory}\"""",
    solve="""cat <<'EOF' | kubectl apply -f -
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: api-vpa
  namespace: vpa-lab
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api
  updatePolicy:
    updateMode: "Off"
  resourcePolicy:
    containerPolicies:
    - containerName: "*"
      minAllowed: {cpu: 25m, memory: 32Mi}
      maxAllowed: {cpu: 500m, memory: 256Mi}
EOF""",
    hints=["`k explain vpa.spec` works because the CRD is installed.", "Quote `\"Off\"`. Unquoted, YAML reads it as false.", "`resourcePolicy.containerPolicies` with `containerName: \"*\"`."],
    solution="""```yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: api-vpa
  namespace: vpa-lab
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api
  updatePolicy:
    updateMode: "Off"
  resourcePolicy:
    containerPolicies:
    - containerName: "*"
      minAllowed: {cpu: 25m, memory: 32Mi}
      maxAllowed: {cpu: 500m, memory: 256Mi}
```""",
    debrief="""# Right-Size the Pods

## What happened
VPA recommends requests from observed usage. Modes:
- `Off`: only recommendations in `.status`.
- `Initial`: applies on pod creation only.
- `Recreate`: evicts pods to apply new values.
- `InPlaceOrRecreate`: uses in-place resize where it can (new with in-place pod resize).

## Exam angle
- VPA is an add-on, not built in. The exam may have it installed and ask for a manifest.
- `"Off"` must be quoted in YAML.
- Do not run HPA on CPU and VPA on CPU for the same Deployment. They fight.

Bookmark: https://kubernetes.io/docs/concepts/workloads/autoscaling/vertical-pod-autoscale/

Your notes: Vertical Pod Autoscaler""")

level(W, "level-91-daemonset", dict(
    name="Every Node, Really Every Node",
    description="The node agent must also run on the control plane",
    objective="Create a DaemonSet that runs on all nodes",
    xp=250, difficulty="intermediate", expected_time="6m", domain="workloads", course_section=3,
    namespace="agent-lab", concepts=["DaemonSet", "tolerations", "control-plane taint"],
    task="""Create DaemonSet **node-agent** in namespace **agent-lab** with image `busybox:1.36`, command `sleep 3600`, label `app=node-agent`.

It must run one pod on **every** node, including the control plane. Requests: CPU 10m, memory 16Mi.""",
    docs=["https://kubernetes.io/docs/concepts/workloads/controllers/daemonset/"]),
    validate="""all_nodes() { [ "$(jp agent-lab ds/node-agent '{.status.numberReady}')" = "$(kubectl get nodes --no-headers | wc -l | tr -d ' ')" ]; }
check 3 "node-agent runs ready on every node" all_nodes
check "requests are 10m / 16Mi" out_eq "10m 16Mi" kubectl get ds node-agent -n agent-lab -o jsonpath='{.spec.template.spec.containers[0].resources.requests.cpu} {.spec.template.spec.containers[0].resources.requests.memory}'
check "the control plane taint is not removed" out_match "node-role.kubernetes.io/control-plane" kubectl get node "$(cq_node_name controlplane)" -o jsonpath='{.spec.taints[*].key}'""",
    solve="""kubectl create deployment node-agent -n agent-lab --image=busybox:1.36 --dry-run=client -o yaml -- sleep 3600 \\
 | "$CQ_ROOT/venv/bin/python3" -c '
import sys, yaml
d = yaml.safe_load(sys.stdin)
d["kind"] = "DaemonSet"
d["spec"].pop("replicas", None); d["spec"].pop("strategy", None); d.pop("status", None)
t = d["spec"]["template"]["spec"]
t["tolerations"] = [{"key": "node-role.kubernetes.io/control-plane", "operator": "Exists", "effect": "NoSchedule"}]
t["containers"][0]["resources"] = {"requests": {"cpu": "10m", "memory": "16Mi"}}
print(yaml.safe_dump(d))' | kubectl apply -f -
kubectl rollout status ds/node-agent -n agent-lab --timeout=120s""",
    hints=["No `k create daemonset`. Generate a Deployment with `$do`, change kind, remove replicas and strategy.",
           "`k describe node <control plane>` shows a NoSchedule taint.", "Add a toleration for `node-role.kubernetes.io/control-plane` with operator Exists."],
    solution="""```bash
k create deploy node-agent -n agent-lab --image=busybox:1.36 $do -- sleep 3600 > ds.yaml
# kind: DaemonSet, delete replicas/strategy/status, then add:
```

```yaml
    spec:
      tolerations:
      - key: node-role.kubernetes.io/control-plane
        operator: Exists
        effect: NoSchedule
      containers:
      - ...
        resources:
          requests: {cpu: 10m, memory: 16Mi}
```""",
    debrief="""# Every Node, Really Every Node

## What happened
A DaemonSet places one pod per eligible node. The control plane has a NoSchedule taint, so without a toleration the DaemonSet skips it. DaemonSets get some tolerations automatically (not-ready, unreachable, disk-pressure), but not this one.

## Exam angle
- The Deployment-to-DaemonSet edit is the standard trick.
- `k get ds` shows DESIRED, CURRENT, READY. DESIRED counts nodes that match.
- Do not remove the control plane taint unless the task says so.

Bookmark: https://kubernetes.io/docs/concepts/workloads/controllers/daemonset/

Your notes: Workloads, Taints and Tolerations""")

level(W, "level-92-cronjob", dict(
    name="Every Five Minutes",
    description="A cleanup job must run on a schedule, and once right now",
    objective="Create a CronJob with history limits and trigger it by hand",
    xp=250, difficulty="intermediate", expected_time="8m", domain="workloads", course_section=5,
    namespace="cron-lab", concepts=["CronJob", "history limits", "kubectl create job --from"],
    task="""In namespace **cron-lab**:
1. Create CronJob **cleanup**: schedule every 5 minutes, image `busybox:1.36`, command `echo cleaning`. Keep **2** successful and **1** failed job in history. Each job gets at most **2** retries and must finish within **60** seconds.
2. Run it once now as Job **cleanup-now**, created from the CronJob.
3. Then suspend the CronJob, so it does not run on its schedule until someone resumes it.""",
    docs=["https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/",
          "https://kubernetes.io/docs/concepts/workloads/controllers/job/"]),
    validate="""J='{.spec.jobTemplate.spec'
check "schedule is */5 * * * *" field_eq cron-lab cj/cleanup '{.spec.schedule}' '*/5 * * * *'
check "history limits 2 / 1" out_eq "2 1" kubectl get cj cleanup -n cron-lab -o jsonpath='{.spec.successfulJobsHistoryLimit} {.spec.failedJobsHistoryLimit}'
check 2 "backoffLimit 2, activeDeadlineSeconds 60" out_eq "2 60" kubectl get cj cleanup -n cron-lab -o jsonpath="$J.backoffLimit} $J.activeDeadlineSeconds}"
check "Job cleanup-now was created from the CronJob" field_eq cron-lab job/cleanup-now '{.metadata.ownerReferences[0].name}' cleanup
check 2 "cleanup-now completed and logged 'cleaning'" out_match cleaning kubectl logs job/cleanup-now -n cron-lab""",
    solve="""kubectl create cronjob cleanup -n cron-lab --image=busybox:1.36 --schedule="*/5 * * * *" --dry-run=client -o yaml -- echo cleaning \\
 | "$CQ_ROOT/venv/bin/python3" -c '
import sys, yaml
c = yaml.safe_load(sys.stdin)
c["spec"]["successfulJobsHistoryLimit"] = 2
c["spec"]["failedJobsHistoryLimit"] = 1
c["spec"]["jobTemplate"]["spec"]["backoffLimit"] = 2
c["spec"]["jobTemplate"]["spec"]["activeDeadlineSeconds"] = 60
print(yaml.safe_dump(c))' | kubectl apply -f -
kubectl create job cleanup-now -n cron-lab --from=cronjob/cleanup
kubectl wait --for=condition=complete job/cleanup-now -n cron-lab --timeout=90s""",
    hints=["`k create cronjob cleanup --image=busybox:1.36 --schedule='*/5 * * * *' $do -- echo cleaning > cj.yaml`.",
           "History limits are in `spec`. backoffLimit and activeDeadlineSeconds are in `spec.jobTemplate.spec`.",
           "`k create job cleanup-now --from=cronjob/cleanup -n cron-lab`."],
    solution="""```bash
k create cronjob cleanup -n cron-lab --image=busybox:1.36 --schedule="*/5 * * * *" $do -- echo cleaning > cj.yaml
# spec.successfulJobsHistoryLimit: 2
# spec.failedJobsHistoryLimit: 1
# spec.jobTemplate.spec.backoffLimit: 2
# spec.jobTemplate.spec.activeDeadlineSeconds: 60
k apply -f cj.yaml
k create job cleanup-now -n cron-lab --from=cronjob/cleanup
k logs job/cleanup-now -n cron-lab
```""",
    debrief="""# Every Five Minutes

## What happened
A CronJob creates a Job on each schedule tick. The Job creates pods. Limits sit on different levels:
- CronJob `spec`: schedule, history limits, concurrencyPolicy, startingDeadlineSeconds, suspend.
- Job spec (`jobTemplate.spec`): backoffLimit, activeDeadlineSeconds, completions, parallelism, ttlSecondsAfterFinished.

## Exam angle
- `k create job <name> --from=cronjob/<cj>` tests a CronJob without waiting.
- `concurrencyPolicy: Forbid` skips a run when the last one is still going.

Bookmark: https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/

Your notes: Workloads""")

level(W, "level-93-secret-volume", dict(
    name="Credentials as Files",
    description="The app reads its password from a file and its settings from env",
    objective="Mount a Secret as a read-only volume and a ConfigMap as env vars",
    xp=250, difficulty="intermediate", expected_time="8m", domain="workloads", course_section=5,
    namespace="config-lab", concepts=["Secret volume", "ConfigMap envFrom", "readOnly", "defaultMode"],
    task="""In namespace **config-lab**:
1. Create Secret **db-creds** with `username=app` and `password=S3cure!`.
2. Create ConfigMap **app-settings** with `LOG_LEVEL=debug` and `REGION=eu-central`.
3. Create pod **app** (image `busybox:1.36`, command `sleep 3600`) that mounts db-creds read-only at `/etc/creds` with file mode **0400**, and loads all keys of app-settings as env vars.""",
    docs=["https://kubernetes.io/docs/concepts/configuration/secret/#using-secrets-as-files-from-a-pod",
          "https://kubernetes.io/docs/tasks/configure-pod-container/configure-pod-configmap/#configure-all-key-value-pairs-in-a-configmap-as-container-environment-variables"]),
    validate="""ex() { kubectl exec app -n config-lab -- sh -c "$1" 2>/dev/null; }
check "secret db-creds has password S3cure!" out_eq 'S3cure!' sh -c "kubectl get secret db-creds -n config-lab -o jsonpath='{.data.password}' | base64 -d"
check 2 "/etc/creds/password has the password" out_eq 'S3cure!' ex 'cat /etc/creds/password'
check "the volume is read-only" out_eq "ro" ex 'grep " /etc/creds " /proc/mounts | grep -o "ro," | head -c2'
check "file mode is 0400" field_eq config-lab pod/app '{.spec.volumes[?(@.secret.secretName=="db-creds")].secret.defaultMode}' 256
check 2 "LOG_LEVEL and REGION are env vars" out_eq "debug eu-central" ex 'echo $LOG_LEVEL $REGION'""",
    solve="""kubectl create secret generic db-creds -n config-lab --from-literal=username=app --from-literal='password=S3cure!'
kubectl create configmap app-settings -n config-lab --from-literal=LOG_LEVEL=debug --from-literal=REGION=eu-central
cat <<'EOF' | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: app
  namespace: config-lab
spec:
  containers:
  - name: app
    image: busybox:1.36
    command: ["sleep", "3600"]
    envFrom:
    - configMapRef: {name: app-settings}
    volumeMounts:
    - name: creds
      mountPath: /etc/creds
      readOnly: true
  volumes:
  - name: creds
    secret:
      secretName: db-creds
      defaultMode: 0400
EOF
kubectl wait --for=condition=Ready pod/app -n config-lab --timeout=60s""",
    hints=["Quote the password in the shell: `--from-literal='password=S3cure!'`. `!` is special in bash.",
           "`envFrom: - configMapRef: name: app-settings` loads all keys.",
           "Volume `secret: secretName: db-creds, defaultMode: 0400`, mount with `readOnly: true`."],
    solution="""```bash
k create secret generic db-creds -n config-lab --from-literal=username=app --from-literal='password=S3cure!'
k create cm app-settings -n config-lab --from-literal=LOG_LEVEL=debug --from-literal=REGION=eu-central
k run app -n config-lab --image=busybox:1.36 $do -- sleep 3600 > app.yaml
```

```yaml
    envFrom:
    - configMapRef: {name: app-settings}
    volumeMounts:
    - {name: creds, mountPath: /etc/creds, readOnly: true}
  volumes:
  - name: creds
    secret: {secretName: db-creds, defaultMode: 0400}
```""",
    debrief="""# Credentials as Files

## What happened
Each Secret key becomes a file in the mount. Mounted Secrets update when the Secret changes (unless subPath). Env vars do not.

## defaultMode
YAML reads `0400` as octal and the API stores decimal 256. In JSON you must write 256. Both mean read-only for the owner.

## Exam angle
- Shell quoting of special characters is a classic trap. Check with `base64 -d`.
- `envFrom` with a ConfigMap or Secret loads all keys. `env.valueFrom` picks one.

Bookmark: https://kubernetes.io/docs/concepts/configuration/secret/

Your notes: Secrets, Config, Environment Variables""")

level(W, "level-94-default-storageclass", dict(
    name="A New Default",
    description="New PVCs without a class should land on a Retain class",
    objective="Create a StorageClass and make it the only default",
    xp=300, difficulty="intermediate", expected_time="8m", domain="storage", course_section=8,
    namespace="sc-lab", concepts=["StorageClass", "default class annotation", "volumeBindingMode", "reclaimPolicy"],
    task="""1. Create StorageClass **local-retain**: provisioner `rancher.io/local-path`, reclaim policy **Retain**, volume binding mode **WaitForFirstConsumer**.
2. Make it the default StorageClass. **standard** must no longer be default. There must be exactly one default.
3. In namespace **sc-lab**, create PVC **data** (1Gi, ReadWriteOnce) **without** a storageClassName, and pod **user** (`busybox:1.36`, `sleep 3600`) that mounts it at `/data`.""",
    docs=["https://kubernetes.io/docs/concepts/storage/storage-classes/",
          "https://kubernetes.io/docs/tasks/administer-cluster/change-default-storage-class/"]),
    setup="kubectl delete storageclass local-retain --ignore-not-found >/dev/null",
    validate="""A='{.metadata.annotations.storageclass\\.kubernetes\\.io/is-default-class}'
defaults() { kubectl get sc -o jsonpath='{range .items[*]}{.metadata.name}={.metadata.annotations.storageclass\\.kubernetes\\.io/is-default-class}{"\\n"}{end}' | grep -c '=true$'; }
check "local-retain: local-path, Retain, WaitForFirstConsumer" out_eq "rancher.io/local-path Retain WaitForFirstConsumer" kubectl get sc local-retain -o jsonpath='{.provisioner} {.reclaimPolicy} {.volumeBindingMode}'
check 2 "local-retain is the default" field_eq - sc/local-retain "$A" true
check "exactly one default StorageClass" out_eq 1 defaults
check "PVC data has no class in the manifest but got local-retain" field_eq sc-lab pvc/data '{.spec.storageClassName}' local-retain
check 2 "PVC data is Bound" field_eq sc-lab pvc/data '{.status.phase}' Bound
check "pod user is Ready" pod_ready sc-lab user""",
    solve="""cat <<'EOF' | kubectl apply -f -
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: local-retain
  annotations:
    storageclass.kubernetes.io/is-default-class: "true"
provisioner: rancher.io/local-path
reclaimPolicy: Retain
volumeBindingMode: WaitForFirstConsumer
EOF
kubectl annotate sc standard storageclass.kubernetes.io/is-default-class=false --overwrite
cat <<'EOF' | kubectl apply -f -
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: data
  namespace: sc-lab
spec:
  accessModes: [ReadWriteOnce]
  resources:
    requests: {storage: 1Gi}
---
apiVersion: v1
kind: Pod
metadata:
  name: user
  namespace: sc-lab
spec:
  containers:
  - name: user
    image: busybox:1.36
    command: ["sleep", "3600"]
    volumeMounts: [{name: data, mountPath: /data}]
  volumes:
  - name: data
    persistentVolumeClaim: {claimName: data}
EOF
kubectl wait --for=condition=Ready pod/user -n sc-lab --timeout=120s""",
    cleanup="""kubectl delete pod user -n sc-lab --ignore-not-found --wait=true --timeout=60s >/dev/null 2>&1
kubectl delete pvc data -n sc-lab --ignore-not-found --timeout=60s >/dev/null 2>&1
for pv in $(kubectl get pv -o jsonpath='{range .items[?(@.spec.storageClassName=="local-retain")]}{.metadata.name}{" "}{end}'); do kubectl delete pv "$pv" --wait=false >/dev/null 2>&1; done
kubectl delete sc local-retain --ignore-not-found >/dev/null 2>&1
kubectl annotate sc standard storageclass.kubernetes.io/is-default-class=true --overwrite >/dev/null 2>&1""",
    hints=["The default is an annotation: `storageclass.kubernetes.io/is-default-class: \"true\"`.",
           "`k annotate sc standard storageclass.kubernetes.io/is-default-class=false --overwrite`.",
           "With WaitForFirstConsumer the PVC stays Pending until the pod is scheduled. That is expected."],
    solution="""```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: local-retain
  annotations:
    storageclass.kubernetes.io/is-default-class: "true"
provisioner: rancher.io/local-path
reclaimPolicy: Retain
volumeBindingMode: WaitForFirstConsumer
```

```bash
k annotate sc standard storageclass.kubernetes.io/is-default-class=false --overwrite
k get sc          # only local-retain shows (default)
```""",
    debrief="""# A New Default

## What happened
A PVC without `storageClassName` gets the default class at creation. If two classes are default, the newest wins, which is confusing. Keep exactly one.

`storageClassName: ""` (empty string) is different: it means "no class, bind to a pre-created PV only".

## Exam angle
- `k get sc` shows `(default)` next to the name.
- StorageClass fields cannot be edited after creation, except annotations and labels. Delete and recreate to change them.
- Retain keeps the PV and its data after the PVC is deleted. Delete removes both.

Bookmark: https://kubernetes.io/docs/tasks/administer-cluster/change-default-storage-class/

Your notes: Storage""")

level(W, "level-95-limitrange", dict(
    name="Defaults for Everyone",
    description="Pods without resources keep landing in the team namespace",
    objective="Set default requests and limits with a LimitRange",
    xp=250, difficulty="intermediate", expected_time="6m", domain="workloads", course_section=3,
    namespace="team-ns", concepts=["LimitRange", "default requests", "max limits"],
    task="""Create LimitRange **container-defaults** in namespace **team-ns** for containers:
- default request: CPU **100m**, memory **64Mi**
- default limit: CPU **200m**, memory **128Mi**
- max: CPU **500m**, memory **256Mi**

Then create pod **plain** (`nginx:1.27-alpine`) with no resources in team-ns.""",
    docs=["https://kubernetes.io/docs/concepts/policy/limit-range/"]),
    validate="""L='{.spec.limits[?(@.type=="Container")]'
R='{.spec.containers[0].resources'
too_big() { ! kubectl run cq-big -n team-ns --image=nginx:1.27-alpine --dry-run=server --overrides='{"spec":{"containers":[{"name":"cq-big","image":"nginx:1.27-alpine","resources":{"limits":{"cpu":"1"}}}]}}' >/dev/null 2>&1; }
check "defaultRequest 100m / 64Mi" out_eq "100m 64Mi" kubectl get limits container-defaults -n team-ns -o jsonpath="$L.defaultRequest.cpu} $L.defaultRequest.memory}"
check "default limit 200m / 128Mi" out_eq "200m 128Mi" kubectl get limits container-defaults -n team-ns -o jsonpath="$L.default.cpu} $L.default.memory}"
check "max 500m / 256Mi" out_eq "500m 256Mi" kubectl get limits container-defaults -n team-ns -o jsonpath="$L.max.cpu} $L.max.memory}"
check 2 "pod plain got the defaults" out_eq "100m 200m 64Mi 128Mi" kubectl get pod plain -n team-ns -o jsonpath="$R.requests.cpu} $R.limits.cpu} $R.requests.memory} $R.limits.memory}"
check "a pod asking for 1 CPU is rejected" too_big""",
    solve="""cat <<'EOF' | kubectl apply -f -
apiVersion: v1
kind: LimitRange
metadata:
  name: container-defaults
  namespace: team-ns
spec:
  limits:
  - type: Container
    defaultRequest: {cpu: 100m, memory: 64Mi}
    default: {cpu: 200m, memory: 128Mi}
    max: {cpu: 500m, memory: 256Mi}
EOF
kubectl run plain -n team-ns --image=nginx:1.27-alpine""",
    hints=["LimitRange fields: `default` (limits), `defaultRequest`, `max`, `min`, under `limits: - type: Container`.",
           "Defaults apply only when a pod is created. Create the pod after the LimitRange.", "`k describe limits -n team-ns`"],
    solution="""```yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: container-defaults
  namespace: team-ns
spec:
  limits:
  - type: Container
    defaultRequest: {cpu: 100m, memory: 64Mi}
    default: {cpu: 200m, memory: 128Mi}
    max: {cpu: 500m, memory: 256Mi}
```

```bash
k run plain -n team-ns --image=nginx:1.27-alpine
k get pod plain -n team-ns -o jsonpath='{.spec.containers[0].resources}'
```""",
    debrief="""# Defaults for Everyone

## What happened
LimitRange is an admission plugin. At pod creation it fills in missing requests and limits, and rejects values outside min and max. Existing pods are not touched.

## LimitRange and ResourceQuota
- LimitRange: per container or pod, defaults and bounds.
- ResourceQuota: total for the namespace. A quota on requests forces every pod to have requests, so the two are often used together.

## Exam angle
- `default` is the limit. `defaultRequest` is the request. The names are easy to swap.

Bookmark: https://kubernetes.io/docs/concepts/policy/limit-range/

Your notes: Resource Requirements, Admission Controllers""")

level(W, "level-96-job-parallel", dict(
    name="Batch Work in Parallel",
    description="Six work items, two workers at a time",
    objective="Write a Job with completions and parallelism",
    xp=200, difficulty="beginner", expected_time="6m", domain="workloads", course_section=5,
    namespace="batch-lab", concepts=["Job", "completions", "parallelism", "backoffLimit", "ttlSecondsAfterFinished"],
    task="""Create Job **process** in namespace **batch-lab** (image `busybox:1.36`, command `sh -c 'echo processing; sleep 5'`):
- **6** completions, **2** pods in parallel
- at most **3** retries
- delete the Job automatically **600** seconds after it finishes""",
    docs=["https://kubernetes.io/docs/concepts/workloads/controllers/job/"]),
    validate="""check "6 completions, parallelism 2" out_eq "6 2" kubectl get job process -n batch-lab -o jsonpath='{.spec.completions} {.spec.parallelism}'
check "backoffLimit 3, ttl 600" out_eq "3 600" kubectl get job process -n batch-lab -o jsonpath='{.spec.backoffLimit} {.spec.ttlSecondsAfterFinished}'
check 3 "the job succeeded 6 times" field_eq batch-lab job/process '{.status.succeeded}' 6""",
    solve="""kubectl create job process -n batch-lab --image=busybox:1.36 --dry-run=client -o yaml -- sh -c 'echo processing; sleep 5' \\
 | "$CQ_ROOT/venv/bin/python3" -c '
import sys, yaml
j = yaml.safe_load(sys.stdin)
j["spec"].update(completions=6, parallelism=2, backoffLimit=3, ttlSecondsAfterFinished=600)
print(yaml.safe_dump(j))' | kubectl apply -f -
kubectl wait --for=condition=complete job/process -n batch-lab --timeout=150s""",
    hints=["`k create job process -n batch-lab --image=busybox:1.36 $do -- sh -c 'echo processing; sleep 5' > job.yaml`.",
           "All four fields go directly under the Job's `spec`.", "Watch it: `k get pods -n batch-lab -w`. Two at a time."],
    solution="""```yaml
spec:
  completions: 6
  parallelism: 2
  backoffLimit: 3
  ttlSecondsAfterFinished: 600
```""",
    debrief="""# Batch Work in Parallel

## What happened
A Job runs pods until `completions` succeed, with at most `parallelism` at once. `backoffLimit` counts failed pods before the Job fails. `ttlSecondsAfterFinished` lets the TTL controller delete it later.

## Exam angle
- Job pod templates need `restartPolicy: Never` or `OnFailure`. `k create job` sets Never.
- `k get job` shows COMPLETIONS as done/total.

Bookmark: https://kubernetes.io/docs/concepts/workloads/controllers/job/

Your notes: Workloads""")
