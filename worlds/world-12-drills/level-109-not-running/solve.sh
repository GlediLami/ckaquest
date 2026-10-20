#!/usr/bin/env bash
source "$CQ_ROOT/lib/common.sh"
kubectl get pods -A --field-selector=status.phase!=Running,status.phase!=Succeeded -o jsonpath='{range .items[*]}{.metadata.namespace}/{.metadata.name}{"\n"}{end}' | grep -v '^kube-system/' > "$CQ_WORK/109/broken.txt"
