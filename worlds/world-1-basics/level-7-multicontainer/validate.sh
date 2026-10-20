#!/bin/bash

echo "🔍 Checking multi-container pod status..."

# Check if pod is running and all containers are ready
POD_STATUS=$(kubectl get pod app-with-logging -n k8squest -o jsonpath='{.status.phase}' 2>/dev/null)
READY_CONTAINERS=$(kubectl get pod app-with-logging -n k8squest -o jsonpath='{.status.containerStatuses[?(@.ready==true)].name}' 2>/dev/null | wc -w | tr -d ' ')
TOTAL_CONTAINERS=$(kubectl get pod app-with-logging -n k8squest -o jsonpath='{.spec.containers[*].name}' 2>/dev/null | wc -w | tr -d ' ')

echo "   Pod Phase: $POD_STATUS"
echo "   Ready containers: $READY_CONTAINERS/$TOTAL_CONTAINERS"

if [[ "$POD_STATUS" == "Running" ]] && [[ "$READY_CONTAINERS" -eq 2 ]]; then
    echo "✅ Pod is running with all 2 containers ready"
    exit 0
else
    echo "❌ Pod status: $POD_STATUS, Ready containers: $READY_CONTAINERS/2"
    echo "💡 Hint: Check logs for each container:"
    echo "   kubectl logs app-with-logging -n k8squest -c main-app"
    echo "   kubectl logs app-with-logging -n k8squest -c log-sidecar"
    exit 1
fi
