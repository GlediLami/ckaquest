#!/bin/bash

# Check service selector
SELECTOR=$(kubectl get service app-service -n k8squest -o jsonpath='{.spec.selector.version}' 2>/dev/null)

# Get endpoint IPs to see which pods are behind the service
ENDPOINTS=$(kubectl get endpoints app-service -n k8squest -o jsonpath='{.subsets[*].addresses[*].ip}' 2>/dev/null | wc -w | tr -d ' ')

if [ "$SELECTOR" = "green" ] && [ "$ENDPOINTS" -gt 0 ]; then
    echo "✅ Service is correctly pointing to GREEN version"
    echo "   Selector: version=$SELECTOR"
    echo "   Endpoints: $ENDPOINTS pods"
    exit 0
else
    if [ "$SELECTOR" != "green" ]; then
        echo "❌ Service is pointing to wrong version!"
        echo "   Current selector: version=$SELECTOR"
        echo "   Should be: version=green"
    fi
    if [ "$ENDPOINTS" -eq 0 ]; then
        echo "❌ Service has no endpoints (no pods match selector)"
    fi
    exit 1
fi
