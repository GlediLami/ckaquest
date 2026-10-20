#!/bin/bash

# Check if using Deployment (not standalone ReplicaSet)
if kubectl get deployment web-app -n k8squest &>/dev/null; then
    READY=$(kubectl get deployment web-app -n k8squest -o jsonpath='{.status.readyReplicas}' 2>/dev/null)
    DESIRED=$(kubectl get deployment web-app -n k8squest -o jsonpath='{.spec.replicas}' 2>/dev/null)
    
    if [ "$READY" = "$DESIRED" ]; then
        echo "✅ Using Deployment (correct approach)"
        echo "   Ready: $READY/$DESIRED pods"
        
        # Check that it's managing ReplicaSets
        RS_COUNT=$(kubectl get replicaset -n k8squest -l app=webapp -o name 2>/dev/null | wc -l | tr -d ' ')
        echo "   Managed ReplicaSets: $RS_COUNT"
        
        exit 0
    else
        echo "⏳ Waiting for Deployment to be ready"
        echo "   Ready: $READY/$DESIRED"
        exit 1
    fi
else
    # Check if still using standalone ReplicaSet
    if kubectl get replicaset web-app-rs -n k8squest &>/dev/null; then
        echo "❌ Still using standalone ReplicaSet"
        echo "   ReplicaSets should be managed by Deployments, not created directly"
        echo ""
        echo "   Problems with standalone ReplicaSets:"
        echo "   - No rolling updates"
        echo "   - No rollback capability"
        echo "   - Can't declaratively update (must create new RS manually)"
        echo ""
        echo "   Convert to Deployment for better management!"
        exit 1
    else
        echo "❌ web-app resource not found"
        exit 1
    fi
fi
