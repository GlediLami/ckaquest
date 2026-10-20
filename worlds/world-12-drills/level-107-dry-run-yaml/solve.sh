#!/usr/bin/env bash
source "$CQ_ROOT/lib/common.sh"
F="$CQ_WORK/107/deploy.yaml"
kubectl create deployment shop -n drill-107 --image=nginx:1.27-alpine --replicas=2 --dry-run=client -o yaml \
 | "$CQ_ROOT/venv/bin/python3" -c '
import sys, yaml
d = yaml.safe_load(sys.stdin)
c = d["spec"]["template"]["spec"]["containers"][0]
c["env"] = [{"name": "MODE", "value": "prod"}]
c["resources"] = {"requests": {"cpu": "50m", "memory": "32Mi"}}
c["readinessProbe"] = {"httpGet": {"path": "/", "port": 80}}
print(yaml.safe_dump(d))' > "$F"
kubectl apply -f "$F"
kubectl rollout status deploy/shop -n drill-107 --timeout=90s
