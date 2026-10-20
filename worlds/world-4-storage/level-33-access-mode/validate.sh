#!/bin/bash

NAMESPACE="ckaquest"
DEPLOYMENT="web-servers"
PVC_NAME="shared-pvc"
PV_NAME="shared-storage"

echo "🔍 Stage 1: Checking if PV exists..."
if ! kubectl get pv "$PV_NAME" &>/dev/null; then
    echo "❌ PersistentVolume '$PV_NAME' not found"
    echo "💡 Hint: Deploy the resources first with 'kubectl apply -f solution.yaml'"
    exit 1
fi
echo "✅ PV exists"

echo ""
echo "🔍 Stage 2: Checking if PVC is bound..."
PVC_STATUS=$(kubectl get pvc "$PVC_NAME" -n "$NAMESPACE" -o jsonpath='{.status.phase}' 2>/dev/null)
if [ "$PVC_STATUS" != "Bound" ]; then
    echo "❌ PVC is not Bound (current: $PVC_STATUS)"
    echo "💡 Hint: PVC should bind to the PV automatically"
    exit 1
fi
echo "✅ PVC is Bound"

echo ""
echo "🔍 Stage 3: Checking PV access mode..."
# Use jq for safer array checking
if ! kubectl get pv "$PV_NAME" -o json | jq -e '.spec.accessModes | index("ReadWriteMany")' &>/dev/null; then
    CURRENT_MODES=$(kubectl get pv "$PV_NAME" -o jsonpath='{.spec.accessModes[*]}')
    echo "❌ PV does not have ReadWriteMany access mode"
    echo "   Current modes: $CURRENT_MODES"
    echo "💡 Hint: For shared storage across multiple nodes, use ReadWriteMany"
    echo "💡 Note: You cannot edit PVC/PV access modes - you must delete and recreate!"
    exit 1
fi
echo "✅ PV has ReadWriteMany access mode"

echo ""
echo "🔍 Stage 4: Checking PVC access mode..."
# Use jq for safer array checking
if ! kubectl get pvc "$PVC_NAME" -n "$NAMESPACE" -o json | jq -e '.spec.accessModes | index("ReadWriteMany")' &>/dev/null; then
    CURRENT_MODES=$(kubectl get pvc "$PVC_NAME" -n "$NAMESPACE" -o jsonpath='{.spec.accessModes[*]}')
    echo "❌ PVC does not have ReadWriteMany access mode"
    echo "   Current modes: $CURRENT_MODES"
    echo "💡 Hint: PVC must match PV access mode"
    echo "💡 Remember: PVC spec is immutable - delete and recreate to change it!"
    exit 1
fi
echo "✅ PVC has ReadWriteMany access mode"

echo ""
echo "🔍 Stage 5: Checking if deployment exists..."
if ! kubectl get deployment "$DEPLOYMENT" -n "$NAMESPACE" &>/dev/null; then
    echo "❌ Deployment '$DEPLOYMENT' not found"
    echo "💡 Hint: Deploy with 'kubectl apply -f solution.yaml'"
    exit 1
fi
echo "✅ Deployment exists"

echo ""
echo "ℹ️  Pod Status (informational only):"
READY_PODS=$(kubectl get deployment "$DEPLOYMENT" -n "$NAMESPACE" -o jsonpath='{.status.readyReplicas}' 2>/dev/null)
DESIRED_PODS=$(kubectl get deployment "$DEPLOYMENT" -n "$NAMESPACE" -o jsonpath='{.spec.replicas}' 2>/dev/null)
echo "   Ready: $READY_PODS/$DESIRED_PODS pods"

if [ "$READY_PODS" = "$DESIRED_PODS" ]; then
    echo "   ✅ All pods are running"
    echo ""
    echo "   💡 Note: In Kind (single-node), pods run even with ReadWriteOnce."
    echo "      Validation checks CONFIGURATION correctness, not runtime behavior."
    echo "      In production multi-node clusters, ReadWriteOnce would prevent"
    echo "      pods on different nodes from mounting the volume!"
else
    echo "   ⚠️  Not all pods are ready yet (this doesn't affect validation)"
fi

echo ""
echo "🎉 SUCCESS! Storage configured correctly with ReadWriteMany!"
echo ""
echo "📚 What you learned:"
echo "   ✅ ReadWriteMany allows multiple nodes to mount the volume"
echo "   ✅ Both PV and PVC must have matching access modes"
echo "   ✅ PVC spec is immutable (requires delete/recreate to change)"
echo "   ✅ Configuration correctness matters even when local tests 'work'"
