#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
J='{.spec.jobTemplate.spec'
check "schedule is */5 * * * *" field_eq cron-lab cj/cleanup '{.spec.schedule}' '*/5 * * * *'
check "history limits 2 / 1" out_eq "2 1" kubectl get cj cleanup -n cron-lab -o jsonpath='{.spec.successfulJobsHistoryLimit} {.spec.failedJobsHistoryLimit}'
check 2 "backoffLimit 2, activeDeadlineSeconds 60" out_eq "2 60" kubectl get cj cleanup -n cron-lab -o jsonpath="$J.backoffLimit} $J.activeDeadlineSeconds}"
check "Job cleanup-now was created from the CronJob" field_eq cron-lab job/cleanup-now '{.metadata.ownerReferences[0].name}' cleanup
check 2 "cleanup-now completed and logged 'cleaning'" out_match cleaning kubectl logs job/cleanup-now -n cron-lab
check "CronJob cleanup is suspended" field_eq cron-lab cj/cleanup '{.spec.suspend}' true
finish
