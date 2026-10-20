#!/usr/bin/env bash
mkdir -p "$CQ_WORK/58"
kubectl top pod -n top-lab --no-headers --sort-by=cpu | head -1 | awk '{print $1}' > "$CQ_WORK/58/cpu-hog.txt"
kubectl top nodes --no-headers --sort-by=cpu | head -1 | awk '{print $1}' > "$CQ_WORK/58/busy-node.txt"
kubectl patch pod report-generator -n top-lab --subresource resize \
  -p '{"spec":{"containers":[{"name":"worker","resources":{"limits":{"cpu":"100m"}}}]}}'
