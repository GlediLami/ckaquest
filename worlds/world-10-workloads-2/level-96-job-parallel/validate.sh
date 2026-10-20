#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
check "6 completions, parallelism 2" out_eq "6 2" kubectl get job process -n batch-lab -o jsonpath='{.spec.completions} {.spec.parallelism}'
check "backoffLimit 3, ttl 600" out_eq "3 600" kubectl get job process -n batch-lab -o jsonpath='{.spec.backoffLimit} {.spec.ttlSecondsAfterFinished}'
check 3 "the job succeeded 6 times" field_eq batch-lab job/process '{.status.succeeded}' 6
finish
