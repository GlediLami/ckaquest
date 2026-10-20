#!/bin/bash

# Level 27 Validation: Cross-namespace Service Communication
# Validates that frontend can access backend service across namespaces

set -e

FRONTEND_NAMESPACE="ckaquest"
BACKEND_NAMESPACE="backend-ns"
FRONTEND_POD="frontend-app"
BACKEND_SERVICE="api-service"

echo "🔍 Level 27: Cross-namespace Service Communication - Validation"
echo "================================================================="
echo ""

# Stage 1: Check if backend namespace exists
echo "Stage 1: Checking backend namespace..."
if ! kubectl get namespace $BACKEND_NAMESPACE &>/dev/null; then
    echo "❌ VALIDATION FAILED!"
    echo ""
    echo "📋 Issue: Namespace '$BACKEND_NAMESPACE' not found"
    echo ""
    echo "💡 Hint: Apply the YAML configuration with: kubectl apply -f solution.yaml"
    exit 1
fi
echo "✅ Backend namespace '$BACKEND_NAMESPACE' exists"
echo ""

# Stage 2: Check if backend service exists
echo "Stage 2: Checking backend service..."
if ! kubectl get service $BACKEND_SERVICE -n $BACKEND_NAMESPACE &>/dev/null; then
    echo "❌ VALIDATION FAILED!"
    echo ""
    echo "📋 Issue: Service '$BACKEND_SERVICE' not found in namespace '$BACKEND_NAMESPACE'"
    echo ""
    echo "💡 Hint: The backend service should be deployed in the backend-ns namespace"
    exit 1
fi
echo "✅ Backend service '$BACKEND_SERVICE' exists in '$BACKEND_NAMESPACE'"
echo ""

# Stage 3: Check backend service has endpoints
echo "Stage 3: Checking backend service endpoints..."
ENDPOINTS=$(kubectl get endpoints $BACKEND_SERVICE -n $BACKEND_NAMESPACE -o jsonpath='{.subsets[*].addresses[*].ip}' 2>/dev/null)

if [ -z "$ENDPOINTS" ]; then
    echo "❌ VALIDATION FAILED!"
    echo ""
    echo "📋 Issue: Backend service has no endpoints (no pods matching selector)"
    echo ""
    echo "💡 Hint: Check if backend pod is running: kubectl get pods -n $BACKEND_NAMESPACE"
    exit 1
fi
echo "✅ Backend service has endpoints: $ENDPOINTS"
echo ""

# Stage 4: Check if frontend pod exists
echo "Stage 4: Checking frontend pod..."
if ! kubectl get pod $FRONTEND_POD -n $FRONTEND_NAMESPACE &>/dev/null; then
    echo "❌ VALIDATION FAILED!"
    echo ""
    echo "📋 Issue: Frontend pod '$FRONTEND_POD' not found in namespace '$FRONTEND_NAMESPACE'"
    echo ""
    echo "💡 Hint: Apply the solution YAML to create the frontend pod"
    exit 1
fi

FRONTEND_STATUS=$(kubectl get pod $FRONTEND_POD -n $FRONTEND_NAMESPACE -o jsonpath='{.status.phase}')
if [ "$FRONTEND_STATUS" != "Running" ]; then
    echo "❌ VALIDATION FAILED!"
    echo ""
    echo "📋 Issue: Frontend pod is in '$FRONTEND_STATUS' state, not 'Running'"
    echo ""
    echo "💡 Hint: Wait for pod to start: kubectl get pod $FRONTEND_POD -n $FRONTEND_NAMESPACE -w"
    exit 1
fi
echo "✅ Frontend pod is running in '$FRONTEND_NAMESPACE'"
echo ""

# Stage 5: Check frontend pod command/args for FQDN
echo "Stage 5: Checking DNS configuration in frontend pod..."
POD_COMMAND=$(kubectl get pod $FRONTEND_POD -n $FRONTEND_NAMESPACE -o jsonpath='{.spec.containers[0].command[2]}')

if echo "$POD_COMMAND" | grep -q "api-service.backend-ns"; then
    if echo "$POD_COMMAND" | grep -q "api-service.backend-ns.svc.cluster.local"; then
        echo "✅ Using full FQDN: api-service.backend-ns.svc.cluster.local (best practice)"
    elif echo "$POD_COMMAND" | grep -q "api-service.backend-ns.svc"; then
        echo "✅ Using FQDN: api-service.backend-ns.svc (works)"
    elif echo "$POD_COMMAND" | grep -q "api-service.backend-ns"; then
        echo "✅ Using namespace-qualified name: api-service.backend-ns (works)"
    fi
elif echo "$POD_COMMAND" | grep -q "http://api-service[^.]"; then
    echo "❌ VALIDATION FAILED!"
    echo ""
    echo "📋 Issue: Frontend is using SHORT NAME 'api-service' instead of FQDN"
    echo ""
    echo "🔍 Current command uses: api-service"
    echo "   This only works within the SAME namespace (ckaquest)"
    echo "   But api-service is in a DIFFERENT namespace (backend-ns)"
    echo ""
    echo "💡 Fix: Use FQDN format: api-service.backend-ns.svc.cluster.local"
    echo ""
    echo "🎯 Kubernetes DNS Format:"
    echo "   Within same namespace:  http://api-service"
    echo "   Cross-namespace:        http://api-service.backend-ns"
    echo "   Full FQDN:              http://api-service.backend-ns.svc.cluster.local"
    echo ""
    echo "🔧 Edit the frontend pod command to use:"
    echo "   wget -q -O- http://api-service.backend-ns.svc.cluster.local"
    exit 1
fi
echo ""

# Stage 6: Wait for frontend to make requests
echo "Stage 6: Waiting for frontend to attempt connection (10 seconds)..."
sleep 10
echo "✅ Frontend should have attempted API calls"
echo ""

# Stage 7: Check frontend logs for successful response
echo "Stage 7: Checking frontend connectivity..."
LOGS=$(kubectl logs $FRONTEND_POD -n $FRONTEND_NAMESPACE --tail=20 2>&1)

if echo "$LOGS" | grep -q "API Response from backend-ns"; then
    echo "✅ Frontend successfully received response from backend!"
elif echo "$LOGS" | grep -iq "could not resolve host\|bad address\|name or service not known"; then
    echo "❌ VALIDATION FAILED!"
    echo ""
    echo "📋 Issue: DNS resolution failed (cannot find service)"
    echo ""
    echo "🔍 Frontend logs show DNS errors:"
    echo "$LOGS" | tail -5
    echo ""
    echo "💡 Hint: The service name doesn't resolve in the frontend's namespace"
    echo "💡 Hint: Use FQDN: api-service.backend-ns.svc.cluster.local"
    echo ""
    echo "🎯 Debug commands:"
    echo "   kubectl logs $FRONTEND_POD -n $FRONTEND_NAMESPACE"
    echo "   kubectl exec $FRONTEND_POD -n $FRONTEND_NAMESPACE -- nslookup api-service"
    echo "   kubectl exec $FRONTEND_POD -n $FRONTEND_NAMESPACE -- nslookup api-service.backend-ns.svc.cluster.local"
    exit 1
elif echo "$LOGS" | grep -iq "connection refused\|connection timed out"; then
    echo "❌ VALIDATION FAILED!"
    echo ""
    echo "📋 Issue: Connection to backend failed"
    echo ""
    echo "🔍 Frontend logs show connection errors:"
    echo "$LOGS" | tail -5
    echo ""
    echo "💡 Hint: DNS resolved but connection failed. Check backend service and pod"
    echo ""
    echo "🎯 Debug commands:"
    echo "   kubectl get service $BACKEND_SERVICE -n $BACKEND_NAMESPACE"
    echo "   kubectl get endpoints $BACKEND_SERVICE -n $BACKEND_NAMESPACE"
    echo "   kubectl get pods -n $BACKEND_NAMESPACE"
    exit 1
else
    echo "⚠️  WARNING: No clear success or failure in logs yet"
    echo "   Recent logs:"
    echo "$LOGS" | tail -5
    echo ""
    echo "💡 Hint: Wait a bit longer or check logs manually:"
    echo "   kubectl logs $FRONTEND_POD -n $FRONTEND_NAMESPACE -f"
    exit 1
fi
echo ""

# Final Success
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                  ✅ VALIDATION PASSED! ✅                     ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "🎉 Excellent work! Cross-namespace communication is working!"
echo ""
echo "📊 What you fixed:"
echo "   • Frontend pod uses FQDN to access backend service"
echo "   • DNS resolves: api-service.backend-ns.svc.cluster.local"
echo "   • Cross-namespace communication successful"
echo "   • Frontend receives: 'API Response from backend-ns'"
echo ""
echo "🎓 Key Concept Mastered:"
echo "   Kubernetes DNS naming:"
echo "   • Same namespace:    http://service-name"
echo "   • Cross-namespace:   http://service-name.namespace"
echo "   • Full FQDN:         http://service-name.namespace.svc.cluster.local"
echo ""
echo "🚀 In production:"
echo "   • Use namespace isolation for security (dev, staging, prod)"
echo "   • Services can communicate across namespaces with FQDN"
echo "   • Use NetworkPolicies to control cross-namespace traffic"
echo "   • Document namespace dependencies"
echo "   • Consider using service mesh for advanced cross-namespace routing"
echo ""

exit 0
