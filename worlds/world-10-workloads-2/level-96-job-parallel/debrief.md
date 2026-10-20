# Batch Work in Parallel

## What happened
A Job runs pods until `completions` succeed, with at most `parallelism` at once. `backoffLimit` counts failed pods before the Job fails. `ttlSecondsAfterFinished` lets the TTL controller delete it later.

## Exam angle
- Job pod templates need `restartPolicy: Never` or `OnFailure`. `k create job` sets Never.
- `k get job` shows COMPLETIONS as done/total.

Bookmark: https://kubernetes.io/docs/concepts/workloads/controllers/job/

Your notes: Workloads
