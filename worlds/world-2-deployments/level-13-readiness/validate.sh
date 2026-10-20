#!/bin/bash

# Check if deployment has readiness probe configured
HAS_READINESS=$(kubectl get deployment slow-startup-app -n k8squest -o jsonpath='{.spec.template.spec.containers[0].readinessProbe}' 2>/dev/null)

if [ -z "$HAS_READINESS" ]; then
    echo "❌ Deployment does not have a readiness probe configured"
    exit 1
fi

# Check if all pods are ready
DESIRED=$(kubectl get deployment slow-startup-app -n k8squest -o jsonpath='{.spec.replicas}' 2>/dev/null)
READY=$(kubectl get deployment slow-startup-app -n k8squest -o jsonpath='{.status.readyReplicas}' 2>/dev/null)

if [ "$READY" = "$DESIRED" ]; then
    echo "✅ All $READY/$DESIRED pods are ready"
    echo "   Readiness probe is configured correctly!"
    exit 0
else
    echo "⏳ Waiting for pods to be ready: $READY/$DESIRED"
    echo "   (This may take 20-30 seconds due to startup delay)"
    exit 1
fi
