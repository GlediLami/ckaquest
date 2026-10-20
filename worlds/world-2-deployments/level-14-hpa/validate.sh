#!/bin/bash

# Check if HPA can get metrics
HPA_STATUS=$(kubectl get hpa web-backend-hpa -n k8squest -o jsonpath='{.status.conditions[?(@.type=="ScalingActive")].status}' 2>/dev/null)

if [ "$HPA_STATUS" = "True" ]; then
    echo "✅ HPA is able to scale (metrics available)"
    
    # Verify metrics-server is running
    METRICS_SERVER=$(kubectl get deployment metrics-server -n kube-system -o jsonpath='{.status.readyReplicas}' 2>/dev/null)
    if [ "$METRICS_SERVER" -ge 1 ]; then
        echo "✅ metrics-server is running"
    fi
    
    # Verify we can get pod metrics
    if kubectl top pods -n k8squest &>/dev/null; then
        echo "✅ Pod metrics are available (kubectl top works)"
    fi
    
    exit 0
else
    echo "❌ HPA cannot scale"
    echo "   ScalingActive status: $HPA_STATUS"
    
    # Check if metrics-server exists
    if ! kubectl get deployment metrics-server -n kube-system &>/dev/null; then
        echo "   ⚠️  metrics-server is not installed!"
        echo "   Install it with: kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml"
        echo "   (For kind/local clusters, you may need to add --kubelet-insecure-tls flag)"
    fi
    
    exit 1
fi
