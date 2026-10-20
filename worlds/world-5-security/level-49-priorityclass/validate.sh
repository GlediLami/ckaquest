#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
check "PriorityClass high-priority has value 1000" field_eq - pc/high-priority "{.value}" 1000
check "PriorityClass low-priority has value 100" field_eq - pc/low-priority "{.value}" 100
check 2 "critical-api runs with high-priority" field_eq priorityclass pod/critical-api "{.spec.priorityClassName}" high-priority
check "critical-api got priority 1000" field_eq priorityclass pod/critical-api "{.spec.priority}" 1000
check "dev-workload-1 runs with low-priority" field_eq priorityclass pod/dev-workload-1 "{.spec.priorityClassName}" low-priority
check "critical-api is Ready" pod_ready priorityclass critical-api
finish
