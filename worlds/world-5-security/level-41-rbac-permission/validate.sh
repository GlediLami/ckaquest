#!/bin/bash

NAMESPACE="ckaquest"
POD_NAME="pod-lister"
SA_NAME="pod-reader"
ROLE_NAME="pod-reader-role"
ROLEBINDING_NAME="pod-reader-binding"

echo "🔍 Stage 1: Checking if ServiceAccount exists..."
if ! kubectl get serviceaccount "$SA_NAME" -n "$NAMESPACE" &>/dev/null; then
    echo "❌ ServiceAccount '$SA_NAME' not found"
    exit 1
fi
echo "✅ ServiceAccount exists"

echo ""
echo "🔍 Stage 2: Checking if Role exists..."
if ! kubectl get role "$ROLE_NAME" -n "$NAMESPACE" &>/dev/null; then
    echo "❌ Role '$ROLE_NAME' not found"
    echo "💡 Hint: Create a Role with permissions to list pods"
    exit 1
fi
echo "✅ Role exists"

echo ""
echo "🔍 Stage 3: Verifying Role has correct permissions..."
ROLE_VERBS=$(kubectl get role "$ROLE_NAME" -n "$NAMESPACE" -o jsonpath='{.rules[0].verbs}' | grep -o 'list')
if [ -z "$ROLE_VERBS" ]; then
    echo "❌ Role missing 'list' permission for pods"
    echo "💡 Hint: Role needs verbs: [get, list, watch]"
    exit 1
fi
echo "✅ Role has list permission"

echo ""
echo "🔍 Stage 4: Checking if RoleBinding exists..."
if ! kubectl get rolebinding "$ROLEBINDING_NAME" -n "$NAMESPACE" &>/dev/null; then
    echo "❌ RoleBinding '$ROLEBINDING_NAME' not found"
    echo "💡 Hint: Create RoleBinding to connect ServiceAccount to Role"
    exit 1
fi
echo "✅ RoleBinding exists"

echo ""
echo "🔍 Stage 5: Verifying RoleBinding connects SA to Role..."
BINDING_ROLE=$(kubectl get rolebinding "$ROLEBINDING_NAME" -n "$NAMESPACE" -o jsonpath='{.roleRef.name}')
BINDING_SA=$(kubectl get rolebinding "$ROLEBINDING_NAME" -n "$NAMESPACE" -o jsonpath='{.subjects[0].name}')

if [ "$BINDING_ROLE" != "$ROLE_NAME" ]; then
    echo "❌ RoleBinding not referencing correct Role (found: $BINDING_ROLE)"
    exit 1
fi

if [ "$BINDING_SA" != "$SA_NAME" ]; then
    echo "❌ RoleBinding not referencing correct ServiceAccount (found: $BINDING_SA)"
    exit 1
fi
echo "✅ RoleBinding correctly configured"

echo ""
echo "🔍 Stage 6: Checking if pod exists..."
if ! kubectl get pod "$POD_NAME" -n "$NAMESPACE" &>/dev/null; then
    echo "❌ Pod '$POD_NAME' not found"
    exit 1
fi
echo "✅ Pod exists"

echo ""
echo "🔍 Stage 7: Checking if pod is Running..."
POD_STATUS=$(kubectl get pod "$POD_NAME" -n "$NAMESPACE" -o jsonpath='{.status.phase}')
if [ "$POD_STATUS" != "Running" ]; then
    echo "❌ Pod is in '$POD_STATUS' state (expected Running)"
    echo "💡 Check logs: kubectl logs $POD_NAME -n $NAMESPACE"
    exit 1
fi
echo "✅ Pod is Running"

echo ""
echo "🔍 Stage 8: Verifying pod successfully lists pods..."
sleep 2  # Give pod time to execute kubectl command
if ! kubectl logs "$POD_NAME" -n "$NAMESPACE" 2>/dev/null | grep -q "Success! Can list pods"; then
    echo "❌ Pod unable to list pods - RBAC permissions not working"
    echo "💡 Check logs: kubectl logs $POD_NAME -n $NAMESPACE"
    exit 1
fi
echo "✅ Pod successfully listed pods with RBAC permissions"

echo ""
echo "🔍 Stage 9: Testing RBAC permissions directly..."
kubectl auth can-i list pods --as=system:serviceaccount:ckaquest:pod-reader -n ckaquest &>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ ServiceAccount cannot list pods according to RBAC check"
    exit 1
fi
echo "✅ RBAC permissions verified with auth can-i"

echo ""
echo "🎉 SUCCESS! ServiceAccount has proper RBAC permissions to list pods!"
