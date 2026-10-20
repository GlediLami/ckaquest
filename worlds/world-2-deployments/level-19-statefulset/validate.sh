#!/bin/bash

# Check if it's a StatefulSet (not Deployment)
if kubectl get statefulset database -n k8squest &>/dev/null; then
    READY=$(kubectl get statefulset database -n k8squest -o jsonpath='{.status.readyReplicas}' 2>/dev/null)
    DESIRED=$(kubectl get statefulset database -n k8squest -o jsonpath='{.spec.replicas}' 2>/dev/null)
    
    if [ "$READY" = "$DESIRED" ]; then
        echo "✅ StatefulSet is correctly configured"
        echo "   Ready: $READY/$DESIRED"
        
        # Verify pod names are stable (database-0, database-1, database-2)
        POD_NAMES=$(kubectl get pods -n k8squest -l app=database -o jsonpath='{.items[*].metadata.name}' 2>/dev/null)
        echo "   Pod names: $POD_NAMES"
        
        # Check if pods have stable names (should contain "-0", "-1", "-2")
        if echo "$POD_NAMES" | grep -q "database-[0-2]"; then
            echo "   ✅ Pods have stable ordinal names"
        fi
        
        exit 0
    else
        echo "⏳ Waiting for StatefulSet to be ready"
        echo "   Ready: $READY/$DESIRED"
        exit 1
    fi
else
    # Check if it's still a Deployment
    if kubectl get deployment database -n k8squest &>/dev/null; then
        echo "❌ Still using Deployment (should be StatefulSet)"
        echo "   Deployments are for stateless apps"
        echo "   Databases need StatefulSets for:"
        echo "   - Stable pod identities"
        echo "   - Persistent storage"
        echo "   - Ordered startup/shutdown"
        exit 1
    else
        echo "❌ database resource not found"
        exit 1
    fi
fi
