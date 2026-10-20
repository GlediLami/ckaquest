#!/usr/bin/env bash
# Apply only the NetworkPolicies from solution.yaml. deny-all stays.
"$CQ_ROOT/venv/bin/python3" - <<'PY' | kubectl apply -f -
import yaml
docs = [d for d in yaml.safe_load_all(open("solution.yaml")) if d and d.get("kind") == "NetworkPolicy"]
print(yaml.safe_dump_all(docs))
PY
