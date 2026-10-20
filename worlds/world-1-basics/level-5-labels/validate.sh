#!/bin/bash

echo "🔍 Checking service and pod status..."

# Check if pod is running
POD_STATUS=$(kubectl get pod backend-app -n ckaquest -o jsonpath='{.status.phase}' 2>/dev/null)
READY=$(kubectl get pod backend-app -n ckaquest -o jsonpath='{.status.containerStatuses[0].ready}' 2>/dev/null)

echo "   Pod Phase: $POD_STATUS"
echo "   Pod Ready: $READY"

# Check if service has endpoints
ENDPOINTS=$(kubectl get endpoints backend-service -n ckaquest -o jsonpath='{.subsets[0].addresses[0].ip}' 2>/dev/null)
echo "   Endpoints: ${ENDPOINTS:-none}"

if [[ "$POD_STATUS" == "Running" ]] && [[ "$READY" == "true" ]] && [[ -n "$ENDPOINTS" ]]; then
    echo "✅ Service successfully connected to pod!"
    exit 0
else
    echo "❌ Service has no endpoints (can't find matching pods)"
    echo "💡 Hint: Check 'kubectl get endpoints backend-service -n ckaquest'"
    echo "💡 Debug: 'kubectl describe service backend-service -n ckaquest'"
    exit 1
fi
