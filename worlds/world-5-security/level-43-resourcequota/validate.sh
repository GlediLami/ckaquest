#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
check "compute-quota is unchanged (requests.cpu 2)" field_eq ckaquest quota/compute-quota "{.spec.hard.requests\.cpu}" 2
check "compute-quota is unchanged (limits.cpu 4)" field_eq ckaquest quota/compute-quota "{.spec.hard.limits\.cpu}" 4
check "resource-hungry-app has requests and limits" field_ne ckaquest pod/resource-hungry-app "{.spec.containers[0].resources.limits.memory}" ""
check 2 "resource-hungry-app is Ready" pod_ready ckaquest resource-hungry-app
finish
