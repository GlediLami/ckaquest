#!/bin/bash

# Level 28 Validation: Service Endpoints Not Updating
# Validates that pods have readiness probes configured

set -e

NAMESPACE="k8squest"
SERVICE_NAME="web-service"

echo "🔍 Level 28: Service Endpoints Not Updating - Validation"
echo "=========================================================="
echo ""

# Stage 1: Check if service exists
echo "Stage 1: Checking Service resource..."
if ! kubectl get service $SERVICE_NAME -n $NAMESPACE &>/dev/null; then
    echo "❌ VALIDATION FAILED!"
    echo ""
    echo "📋 Issue: Service '$SERVICE_NAME' not found in namespace '$NAMESPACE'"
    echo ""
    echo "💡 Hint: Apply the YAML configuration with: kubectl apply -f solution.yaml"
    exit 1
fi
echo "✅ Service '$SERVICE_NAME' exists"
echo ""

# Stage 2: Check if backend pods exist
echo "Stage 2: Checking backend pods..."
PODS=$(kubectl get pods -n $NAMESPACE -l app=web --no-headers 2>/dev/null | awk '{print $1}')
POD_COUNT=$(echo "$PODS" | grep -c "web-app" || echo "0")

if [ "$POD_COUNT" -lt "1" ]; then
    echo "❌ VALIDATION FAILED!"
    echo ""
    echo "📋 Issue: No backend pods found with label 'app=web'"
    echo ""
    echo "💡 Hint: Apply the solution YAML to create pods"
    exit 1
fi
echo "✅ Found $POD_COUNT backend pod(s)"
echo ""

# Stage 3: Check readiness probes on each pod
echo "Stage 3: Checking readiness probes..."
HAS_READINESS_PROBE=true

for POD in $PODS; do
    if echo "$POD" | grep -q "web-app"; then
        READINESS_PROBE=$(kubectl get pod $POD -n $NAMESPACE -o jsonpath='{.spec.containers[0].readinessProbe}' 2>/dev/null)
        
        if [ -z "$READINESS_PROBE" ] || [ "$READINESS_PROBE" = "{}" ]; then
            echo "❌ VALIDATION FAILED!"
            echo ""
            echo "📋 Issue: Pod '$POD' is MISSING a readiness probe"
            echo ""
            echo "🔍 Why this matters:"
            echo "   Without a readiness probe, Kubernetes immediately adds the pod"
            echo "   to service endpoints, even if the application isn't ready yet."
            echo ""
            echo "   Result:"
            echo "   • Traffic sent to pods during initialization → errors"
            echo "   • Traffic sent to unhealthy pods → errors"
            echo "   • No automatic endpoint removal when pods fail"
            echo ""
            echo "💡 Fix: Add a readiness probe to the pod spec:"
            echo "   spec:"
            echo "     containers:"
            echo "     - name: app"
            echo "       readinessProbe:"
            echo "         httpGet:"
            echo "           path: /"
            echo "           port: 8080"
            echo "         initialDelaySeconds: 5"
            echo "         periodSeconds: 5"
            echo ""
            echo "🎯 What to check:"
            echo "   kubectl describe pod $POD -n $NAMESPACE | grep -A10 Readiness"
            HAS_READINESS_PROBE=false
            exit 1
        fi
        
        # Check probe type
        PROBE_TYPE=""
        if echo "$READINESS_PROBE" | grep -q "httpGet"; then
            PROBE_TYPE="HTTP"
        elif echo "$READINESS_PROBE" | grep -q "tcpSocket"; then
            PROBE_TYPE="TCP"
        elif echo "$READINESS_PROBE" | grep -q "exec"; then
            PROBE_TYPE="Exec"
        fi
        
        echo "✅ Pod '$POD' has readiness probe ($PROBE_TYPE)"
    fi
done
echo ""

# Stage 4: Wait for pods to be ready
echo "Stage 4: Waiting for pods to become ready..."
TIMEOUT=30
ELAPSED=0

while [ $ELAPSED -lt $TIMEOUT ]; do
    READY_COUNT=$(kubectl get pods -n $NAMESPACE -l app=web --field-selector=status.phase=Running 2>/dev/null | grep -c "1/1" || echo "0")
    
    if [ "$READY_COUNT" -eq "$POD_COUNT" ]; then
        echo "✅ All $POD_COUNT pod(s) are ready"
        break
    fi
    
    sleep 2
    ELAPSED=$((ELAPSED + 2))
done

if [ $ELAPSED -ge $TIMEOUT ]; then
    echo "⚠️  WARNING: Pods not all ready after ${TIMEOUT}s"
    echo "   This might be normal if pods are still initializing"
    echo ""
    kubectl get pods -n $NAMESPACE -l app=web
    echo ""
fi
echo ""

# Stage 5: Check service endpoints
echo "Stage 5: Checking service endpoints..."
ENDPOINTS=$(kubectl get endpoints $SERVICE_NAME -n $NAMESPACE -o jsonpath='{.subsets[*].addresses[*].ip}' 2>/dev/null)

if [ -z "$ENDPOINTS" ]; then
    echo "⚠️  WARNING: Service has no endpoints yet"
    echo "   Pods might still be initializing or readiness probes failing"
    echo ""
    echo "🔍 Debug:"
    echo "   kubectl get endpoints $SERVICE_NAME -n $NAMESPACE"
    echo "   kubectl describe pod -n $NAMESPACE -l app=web | grep -A5 Conditions"
    echo ""
else
    ENDPOINT_COUNT=$(echo "$ENDPOINTS" | wc -w | tr -d ' ')
    echo "✅ Service has $ENDPOINT_COUNT endpoint(s): $ENDPOINTS"
fi
echo ""

# Stage 6: Verify endpoints match ready pods
echo "Stage 6: Verifying endpoints match ready pods..."

# Robust comparison: sort and compare IPs, ignore whitespace/order
READY_PODS=$(kubectl get pods -n $NAMESPACE -l app=web -o jsonpath='{range .items[?(@.status.conditions[?(@.type=="Ready")].status=="True")]}{.status.podIP}{"\n"}{end}' 2>/dev/null | sort)
ENDPOINTS_SORTED=$(echo "$ENDPOINTS" | tr ' ' '\n' | sort)

if [ -n "$READY_PODS" ] && [ -n "$ENDPOINTS_SORTED" ]; then
    DIFF=$(diff <(echo "$READY_PODS") <(echo "$ENDPOINTS_SORTED"))
    if [ -z "$DIFF" ]; then
        echo "✅ Endpoints exactly match ready pod IPs"
    else
        echo "❌ Endpoint IPs do not match ready pod IPs!"
        echo "Ready pods: $READY_PODS"
        echo "Endpoints: $ENDPOINTS_SORTED"
        echo "$DIFF"
        exit 1
    fi
else
    echo "ℹ️  Pods still initializing, endpoints will update when ready"
fi
echo ""

# Final Success
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                  ✅ VALIDATION PASSED! ✅                     ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "🎉 Excellent work! Your pods have readiness probes configured!"
echo ""
echo "📊 What you fixed:"
echo "   • Added readiness probes to pod specifications"
echo "   • Kubernetes now checks if pods are ready before routing traffic"
echo "   • Service endpoints automatically update based on readiness"
echo "   • No traffic sent to pods during initialization"
echo ""
echo "🎓 Key Concept Mastered:"
echo "   Readiness probes tell Kubernetes when a pod is ready to serve traffic."
echo "   • Pod starts → Readiness probe fails → NOT in endpoints → No traffic"
echo "   • App initializes → Readiness probe succeeds → Added to endpoints → Traffic flows"
echo "   • App becomes unhealthy → Probe fails → Removed from endpoints → No traffic"
echo ""
echo "🚀 In production:"
echo "   • Always configure readiness probes for services"
echo "   • Use appropriate probe type: HTTP (APIs), TCP (databases), Exec (custom)"
echo "   • Set initialDelaySeconds to allow app startup time"
echo "   • Use failureThreshold to avoid flapping (add/remove from endpoints)"
echo "   • Different from liveness probes (liveness restarts pod, readiness removes from endpoints)"
echo ""
echo "⚖️  Readiness vs Liveness:"
echo "   • Readiness: Is the app ready to serve traffic? (controls endpoints)"
echo "   • Liveness: Is the app still alive? (controls restarts)"
echo "   • Use both for robust health checking!"
echo ""

exit 0
