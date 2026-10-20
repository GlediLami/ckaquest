#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
busiest_node() { kubectl top nodes --no-headers --sort-by=cpu | head -1 | awk '{print $1}'; }
node_matches() { [ "$(sed -e 's/[[:space:]]*$//' "$CQ_WORK/58/busy-node.txt")" = "$(busiest_node)" ]; }
check 2 "cpu-hog.txt names the CPU hog" file_eq "$CQ_WORK/58/cpu-hog.txt" report-generator
check "busy-node.txt names the busiest node" node_matches
check 2 "report-generator CPU limit is 100m" field_eq top-lab pod/report-generator '{.spec.containers[0].resources.limits.cpu}' 100m
check "report-generator was resized, not recreated (restartCount 0)" field_eq top-lab pod/report-generator '{.status.containerStatuses[0].restartCount}' 0
check "the running container got the new limit" field_eq top-lab pod/report-generator '{.status.containerStatuses[0].resources.limits.cpu}' 100m
finish
