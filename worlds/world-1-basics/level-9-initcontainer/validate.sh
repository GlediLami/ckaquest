#!/bin/bash

echo "🔍 Checking pod and init container status..."

POD_STATUS=$(kubectl get pod web-with-init -n ckaquest -o jsonpath='{.status.phase}' 2>/dev/null)
READY=$(kubectl get pod web-with-init -n ckaquest -o jsonpath='{.status.containerStatuses[0].ready}' 2>/dev/null)
INIT_STATUS=$(kubectl get pod web-with-init -n ckaquest -o jsonpath='{.status.initContainerStatuses[0].state}' 2>/dev/null)

echo "   Pod Phase: $POD_STATUS"
echo "   Ready: $READY"

if [[ "$POD_STATUS" == "Running" ]] && [[ "$READY" == "true" ]]; then
    echo "✅ Pod successfully initialized and running"
    exit 0
else
    echo "❌ Pod status: $POD_STATUS (Ready: $READY)"
    echo "💡 Hint: Check init container logs:"
    echo "   kubectl logs web-with-init -n ckaquest -c wait-for-service"
    echo "   kubectl describe pod web-with-init -n ckaquest"
    exit 1
fi
