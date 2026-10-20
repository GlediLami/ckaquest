#!/bin/bash

# Get replica counts
STABLE=$(kubectl get deployment app-stable -n k8squest -o jsonpath='{.status.readyReplicas}' 2>/dev/null)
CANARY=$(kubectl get deployment app-canary -n k8squest -o jsonpath='{.status.readyReplicas}' 2>/dev/null)

TOTAL=$((STABLE + CANARY))
if [ "$TOTAL" -eq 0 ]; then
    echo "❌ No pods are ready"
    exit 1
fi

# Calculate percentages
CANARY_PERCENT=$((CANARY * 100 / TOTAL))

# Target: 10% canary (±2% tolerance)
if [ "$CANARY_PERCENT" -ge 8 ] && [ "$CANARY_PERCENT" -le 12 ]; then
    echo "✅ Canary traffic split is correct"
    echo "   Stable: $STABLE pods (~$((STABLE * 100 / TOTAL))%)"
    echo "   Canary: $CANARY pods (~$CANARY_PERCENT%)"
    echo "   Total: $TOTAL pods"
    exit 0
else
    echo "❌ Canary traffic split is wrong"
    echo "   Stable: $STABLE pods (~$((STABLE * 100 / TOTAL))%)"
    echo "   Canary: $CANARY pods (~$CANARY_PERCENT%)"
    echo "   Target: ~10% canary (1 canary pod for every 9 stable pods)"
    exit 1
fi
