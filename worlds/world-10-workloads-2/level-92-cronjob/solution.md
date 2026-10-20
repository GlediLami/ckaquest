# Solution

```bash
k create cronjob cleanup -n cron-lab --image=busybox:1.36 --schedule="*/5 * * * *" $do -- echo cleaning > cj.yaml
# spec.successfulJobsHistoryLimit: 2
# spec.failedJobsHistoryLimit: 1
# spec.jobTemplate.spec.backoffLimit: 2
# spec.jobTemplate.spec.activeDeadlineSeconds: 60
k apply -f cj.yaml
k create job cleanup-now -n cron-lab --from=cronjob/cleanup
k logs job/cleanup-now -n cron-lab
```
