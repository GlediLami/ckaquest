#!/bin/bash

echo "🔍 Checking pod and service configuration..."

# Check if pod is running
POD_STATUS=$(kubectl get pod web-server -n k8squest -o jsonpath='{.status.phase}' 2>/dev/null)
READY=$(kubectl get pod web-server -n k8squest -o jsonpath='{.status.containerStatuses[0].ready}' 2>/dev/null)

echo "   Pod Phase: $POD_STATUS"
echo "   Pod Ready: $READY"

# Check service targetPort
SERVICE_PORT=$(kubectl get service web-service -n k8squest -o jsonpath='{.spec.ports[0].targetPort}' 2>/dev/null)
echo "   Service targetPort: $SERVICE_PORT"

# Check endpoints
ENDPOINTS=$(kubectl get endpoints web-service -n k8squest -o jsonpath='{.subsets[0].addresses[0].ip}' 2>/dev/null)
echo "   Endpoints: ${ENDPOINTS:-none}"

if [[ "$POD_STATUS" == "Running" ]] && [[ "$READY" == "true" ]] && [[ "$SERVICE_PORT" == "80" ]] && [[ -n "$ENDPOINTS" ]]; then
    echo "✅ Service targetPort correctly configured and connected to pod"
    exit 0
else
    if [[ "$SERVICE_PORT" != "80" ]]; then
        echo "❌ Service targetPort is $SERVICE_PORT (should be 80)"
        echo "💡 Hint: The nginx container listens on port 80, not $SERVICE_PORT"
    else
        echo "❌ Configuration issue detected"
    fi
    echo "💡 Check: kubectl describe service web-service -n k8squest"
    exit 1
fi
