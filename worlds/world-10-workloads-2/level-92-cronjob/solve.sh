#!/usr/bin/env bash
source "$CQ_ROOT/lib/common.sh"
kubectl create cronjob cleanup -n cron-lab --image=busybox:1.36 --schedule="*/5 * * * *" --dry-run=client -o yaml -- echo cleaning \
 | "$CQ_ROOT/venv/bin/python3" -c '
import sys, yaml
c = yaml.safe_load(sys.stdin)
c["spec"]["successfulJobsHistoryLimit"] = 2
c["spec"]["failedJobsHistoryLimit"] = 1
c["spec"]["jobTemplate"]["spec"]["backoffLimit"] = 2
c["spec"]["jobTemplate"]["spec"]["activeDeadlineSeconds"] = 60
print(yaml.safe_dump(c))' | kubectl apply -f -
kubectl create job cleanup-now -n cron-lab --from=cronjob/cleanup
kubectl wait --for=condition=complete job/cleanup-now -n cron-lab --timeout=90s
kubectl patch cronjob cleanup -n cron-lab -p '{"spec":{"suspend":true}}'
