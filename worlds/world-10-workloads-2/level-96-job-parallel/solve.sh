#!/usr/bin/env bash
source "$CQ_ROOT/lib/common.sh"
kubectl create job process -n batch-lab --image=busybox:1.36 --dry-run=client -o yaml -- sh -c 'echo processing; sleep 5' \
 | "$CQ_ROOT/venv/bin/python3" -c '
import sys, yaml
j = yaml.safe_load(sys.stdin)
j["spec"].update(completions=6, parallelism=2, backoffLimit=3, ttlSecondsAfterFinished=600)
print(yaml.safe_dump(j))' | kubectl apply -f -
kubectl wait --for=condition=complete job/process -n batch-lab --timeout=150s
