#!/bin/bash

# Check if deployment is healthy (all replicas ready)
READY_REPLICAS=$(kubectl get deployment web-app -n k8squest -o jsonpath='{.status.readyReplicas}' 2>/dev/null)
DESIRED_REPLICAS=$(kubectl get deployment web-app -n k8squest -o jsonpath='{.spec.replicas}' 2>/dev/null)

# Also check that we're not on the broken image
CURRENT_IMAGE=$(kubectl get deployment web-app -n k8squest -o jsonpath='{.spec.template.spec.containers[0].image}' 2>/dev/null)

if [ "$READY_REPLICAS" = "$DESIRED_REPLICAS" ] && [ "$READY_REPLICAS" -gt 0 ] && [[ ! "$CURRENT_IMAGE" =~ "nonexistent" ]]; then
    echo "✅ Deployment is healthy with $READY_REPLICAS/$DESIRED_REPLICAS ready replicas"
    echo "   Image successfully rolled back to: $CURRENT_IMAGE"
    exit 0
else
    echo "❌ Deployment not healthy"
    echo "   Ready replicas: $READY_REPLICAS, Desired: $DESIRED_REPLICAS"
    echo "   Current image: $CURRENT_IMAGE"
    if [[ "$CURRENT_IMAGE" =~ "nonexistent" ]]; then
        echo "   ⚠️  Still using the broken image!"
    fi
    exit 1
fi
