#!/usr/bin/env bash
source "$CQ_ROOT/lib/common.sh"
kubectl get nodes -o jsonpath='{range .items[*]}{.metadata.name} {.status.addresses[?(@.type=="InternalIP")].address}{"\n"}{end}' > "$CQ_WORK/103/nodes.txt"
