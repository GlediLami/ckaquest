#!/bin/bash

# Check if pods are running and NOT constantly restarting
RESTART_COUNT=$(kubectl get pods -n k8squest -l app=api -o jsonpath='{.items[*].status.containerStatuses[*].restartCount}' 2>/dev/null | awk '{for(i=1;i<=NF;i++) sum+=$i} END {print sum}')
RUNNING_PODS=$(kubectl get pods -n k8squest -l app=api -o jsonpath='{.items[?(@.status.phase=="Running")].metadata.name}' 2>/dev/null | wc -w | tr -d ' ')

# Give a grace period - if restarts are low (< 3 total) and pods are running, consider it fixed
if [ "$RUNNING_PODS" -eq 2 ] && [ "$RESTART_COUNT" -lt 3 ]; then
    echo "✅ Pods are running stably with $RUNNING_PODS/2 ready"
    echo "   Total restart count: $RESTART_COUNT (healthy)"
    exit 0
else
    echo "❌ Pods are not healthy"
    echo "   Running pods: $RUNNING_PODS/2"
    echo "   Total restarts: $RESTART_COUNT"
    if [ "$RESTART_COUNT" -ge 3 ]; then
        echo "   ⚠️  Too many restarts - liveness probe likely failing!"
    fi
    exit 1
fi
