#!/usr/bin/env bash
source "$CQ_ROOT/lib/common.sh"
kubectl create deployment node-agent -n agent-lab --image=busybox:1.36 --dry-run=client -o yaml -- sleep 3600 \
 | "$CQ_ROOT/venv/bin/python3" -c '
import sys, yaml
d = yaml.safe_load(sys.stdin)
d["kind"] = "DaemonSet"
d["spec"].pop("replicas", None); d["spec"].pop("strategy", None); d.pop("status", None)
t = d["spec"]["template"]["spec"]
t["tolerations"] = [{"key": "node-role.kubernetes.io/control-plane", "operator": "Exists", "effect": "NoSchedule"}]
t["containers"][0]["resources"] = {"requests": {"cpu": "10m", "memory": "16Mi"}}
print(yaml.safe_dump(d))' | kubectl apply -f -
kubectl rollout status ds/node-agent -n agent-lab --timeout=120s
