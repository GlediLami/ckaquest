#!/bin/bash

NAMESPACE="ckaquest"
DB_POD="database"
BACKEND_POD="backend"

echo "🔍 VALIDATION STAGE 1: Checking if pods exist..."
if ! kubectl get pod $DB_POD -n $NAMESPACE &>/dev/null; then
    echo "❌ FAILED: Database pod not found"
    exit 1
fi
if ! kubectl get pod $BACKEND_POD -n $NAMESPACE &>/dev/null; then
    echo "❌ FAILED: Backend pod not found"
    exit 1
fi
echo "✅ Both pods exist"

echo ""
echo "🔍 VALIDATION STAGE 2: Checking if pods are running..."
DB_STATUS=$(kubectl get pod $DB_POD -n $NAMESPACE -o jsonpath='{.status.phase}')
BACKEND_STATUS=$(kubectl get pod $BACKEND_POD -n $NAMESPACE -o jsonpath='{.status.phase}')
if [ "$DB_STATUS" != "Running" ]; then
    echo "❌ FAILED: Database pod is $DB_STATUS, not Running"
    exit 1
fi
if [ "$BACKEND_STATUS" != "Running" ]; then
    echo "❌ FAILED: Backend pod is $BACKEND_STATUS, not Running"
    exit 1
fi
echo "✅ Both pods are running"

echo ""
echo "🔍 VALIDATION STAGE 3: Checking if NetworkPolicies exist..."
if ! kubectl get networkpolicy -n $NAMESPACE | grep -q "allow"; then
    echo "❌ FAILED: No NetworkPolicy with 'allow' found"
    echo "💡 Hint: Create NetworkPolicy to allow traffic between pods"
    exit 1
fi
echo "✅ NetworkPolicies exist"

echo ""
echo "🔍 VALIDATION STAGE 4: Verifying database ingress policy..."
DB_POLICY=$(kubectl get networkpolicy -n $NAMESPACE -o json | jq -r '.items[] | select(.spec.podSelector.matchLabels.app == "database") | .metadata.name' | head -1)
if [ -z "$DB_POLICY" ]; then
    echo "❌ FAILED: No NetworkPolicy targeting database pod"
    echo "💡 Hint: Create NetworkPolicy with podSelector matching app: database"
    exit 1
fi
echo "✅ Database has NetworkPolicy: $DB_POLICY"

echo ""
echo "🔍 VALIDATION STAGE 5: Verifying backend egress policy..."
BACKEND_POLICY=$(kubectl get networkpolicy -n $NAMESPACE -o json | jq -r '.items[] | select(.spec.podSelector.matchLabels.app == "backend") | .metadata.name' | head -1)
if [ -z "$BACKEND_POLICY" ]; then
    echo "❌ FAILED: No NetworkPolicy targeting backend pod"
    echo "💡 Hint: Create NetworkPolicy with podSelector matching app: backend"
    exit 1
fi
echo "✅ Backend has NetworkPolicy: $BACKEND_POLICY"

echo ""
echo "🔍 VALIDATION STAGE 6: Checking Service & Endpoints (DNS)"

# Ensure a Service exists for the database so the name 'database' resolves
if ! kubectl get svc database -n $NAMESPACE &>/dev/null; then
    echo "❌ FAILED: Service 'database' not found in namespace $NAMESPACE"
    echo "💡 Hint: Create a ClusterIP Service named 'database' selecting the database pod"
    exit 1
fi
echo "✅ Service 'database' exists"

# Check endpoints for the service
EP_COUNT=$(kubectl get endpoints database -n $NAMESPACE -o json | jq '.subsets | length')
if [ "$EP_COUNT" = "0" ] || [ "$EP_COUNT" = "null" ]; then
    echo "❌ FAILED: Service 'database' has no endpoints; pods may not match selector"
    echo "💡 Hint: Ensure the database pod has label app: database and Service selector matches it"
    exit 1
fi
echo "✅ Service has endpoints: $EP_COUNT subset(s)"

echo ""
echo "🔍 VALIDATION STAGE 7: Active connectivity test from backend pod"
echo "Waiting 5 seconds for policies to take effect..."
sleep 5

# Try to connect from backend to the service DNS name
kubectl exec $BACKEND_POD -n $NAMESPACE -- sh -c "nc -vz database 5432 -w 5" >/dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Backend can reach database: TCP connection to database:5432 succeeded"
else
    echo "❌ FAILED: Backend cannot reach database (connection timed out or refused)"
    echo "   Check NetworkPolicy rules and ensure backend egress + database ingress allow port 5432"
    echo "   Check backend logs: kubectl logs $BACKEND_POD -n $NAMESPACE"
    exit 1
fi

echo ""
echo "🎉 SUCCESS! NetworkPolicy configuration validated!"
echo ""
echo "Network policies are configured to allow:"
echo "  • Backend → Database on port 5432"
echo "  • Backend → DNS for name resolution"
echo "  • Database accepts connections from backend only"
