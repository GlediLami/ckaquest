#!/bin/bash

# Check if service has endpoints
ENDPOINTS=$(kubectl get endpoints backend-service -n k8squest -o jsonpath='{.subsets[*].addresses[*].ip}' 2>/dev/null)

if [[ -z "$ENDPOINTS" ]]; then
  echo "❌ Service has no endpoints. Check the selector!"
  exit 1
fi

# Test connectivity from test-client pod
RESPONSE=$(kubectl exec test-client -n k8squest -- curl -s -o /dev/null -w "%{http_code}" http://backend-service 2>/dev/null)

if [[ "$RESPONSE" == "200" ]]; then
  echo "✅ Level complete! Service is routing traffic correctly"
  exit 0
else
  echo "❌ Service unreachable. Response code: $RESPONSE"
  exit 1
fi
