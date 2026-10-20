# Every Five Minutes

## What happened
A CronJob creates a Job on each schedule tick. The Job creates pods. Limits sit on different levels:
- CronJob `spec`: schedule, history limits, concurrencyPolicy, startingDeadlineSeconds, suspend.
- Job spec (`jobTemplate.spec`): backoffLimit, activeDeadlineSeconds, completions, parallelism, ttlSecondsAfterFinished.

## Exam angle
- `k create job <name> --from=cronjob/<cj>` tests a CronJob without waiting.
- `concurrencyPolicy: Forbid` skips a run when the last one is still going.

Bookmark: https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/

Your notes: Workloads
