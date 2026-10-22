#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
N1="$(cq_node_name node01)"
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
check 3 "each pod requests about a third of node01's free CPU and memory" fair
finish
