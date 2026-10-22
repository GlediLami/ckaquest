#!/usr/bin/env bash
source "$CQ_ROOT/lib/common.sh"
N1="$(cq_node_name node01)"
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
kubectl rollout status deploy/wordpress -n resource-lab --timeout=120s
