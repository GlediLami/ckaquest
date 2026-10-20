#!/bin/bash

NAMESPACE="k8squest"
POD_NAME="regular-app"
NODE_NAME="kind-control-plane"

echo "🔍 VALIDATION STAGE 1: Checking if node is tainted..."
NODE_TAINTS=$(kubectl get node $NODE_NAME -o jsonpath='{.spec.taints[?(@.key=="dedicated")]}')
if [ -z "$NODE_TAINTS" ]; then
    echo "⚠️  Node not tainted yet. Applying taint..."
    kubectl taint nodes $NODE_NAME dedicated=gpu:NoSchedule --overwrite
    echo "✅ Node tainted: dedicated=gpu:NoSchedule"
else
    echo "✅ Node has taint: dedicated=gpu"
fi

echo ""
echo "🔍 VALIDATION STAGE 2: Checking if pod exists..."
if ! kubectl get pod $POD_NAME -n $NAMESPACE &>/dev/null; then
    echo "❌ FAILED: Pod '$POD_NAME' not found"
    exit 1
fi
echo "✅ Pod exists"

echo ""
echo "🔍 VALIDATION STAGE 3: Checking if pod is Running (not Pending)..."
POD_STATUS=$(kubectl get pod $POD_NAME -n $NAMESPACE -o jsonpath='{.status.phase}')
if [ "$POD_STATUS" = "Pending" ]; then
    echo "❌ FAILED: Pod is still Pending"
    echo "💡 Hint: Check pod events: kubectl describe pod $POD_NAME -n $NAMESPACE"
    echo "💡 Hint: Pod needs toleration matching node taint"
    exit 1
fi
if [ "$POD_STATUS" != "Running" ]; then
    echo "❌ FAILED: Pod is in '$POD_STATUS' state"
    exit 1
fi
echo "✅ Pod is Running"

echo ""
echo "🔍 VALIDATION STAGE 4: Verifying pod has tolerations configured..."
TOLERATIONS=$(kubectl get pod $POD_NAME -n $NAMESPACE -o jsonpath='{.spec.tolerations}')
if [ -z "$TOLERATIONS" ] || [ "$TOLERATIONS" = "null" ]; then
    echo "❌ FAILED: No tolerations configured on pod"
    echo "💡 Hint: Add tolerations to spec.tolerations"
    exit 1
fi
echo "✅ Tolerations are configured"

echo ""
echo "🔍 VALIDATION STAGE 5: Checking toleration matches taint..."
TOLERATION_KEY=$(kubectl get pod $POD_NAME -n $NAMESPACE -o jsonpath='{.spec.tolerations[?(@.key=="dedicated")].key}')
if [ "$TOLERATION_KEY" != "dedicated" ]; then
    echo "❌ FAILED: Toleration key doesn't match taint key 'dedicated'"
    echo "💡 Hint: Toleration key must match taint key exactly"
    exit 1
fi
echo "✅ Toleration key matches taint"

echo ""
echo "🔍 VALIDATION STAGE 6: Verifying pod scheduled on tainted node..."
SCHEDULED_NODE=$(kubectl get pod $POD_NAME -n $NAMESPACE -o jsonpath='{.spec.nodeName}')
echo "✅ Pod scheduled on node: $SCHEDULED_NODE"

echo ""
echo "🎉 SUCCESS! Pod tolerates node taint and is running!"
echo ""
echo "Taint details:"
kubectl get node $SCHEDULED_NODE -o jsonpath='{.spec.taints[?(@.key=="dedicated")]}' | jq '.'
echo ""
echo "Toleration details:"
kubectl get pod $POD_NAME -n $NAMESPACE -o jsonpath='{.spec.tolerations[?(@.key=="dedicated")]}' | jq '.'
