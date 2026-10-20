#!/bin/bash

NAMESPACE="k8squest"
PV_NAME="important-data"
PVC_NAME="data-claim"
POD_NAME="data-writer"

echo "🔍 Stage 1: Checking if PV exists..."
if ! kubectl get pv "$PV_NAME" &>/dev/null; then
    echo "❌ PersistentVolume '$PV_NAME' not found"
    exit 1
fi
echo "✅ PV exists"

echo ""
echo "🔍 Stage 2: Checking PV reclaim policy..."
RECLAIM_POLICY=$(kubectl get pv "$PV_NAME" -o jsonpath='{.spec.persistentVolumeReclaimPolicy}')
if [ "$RECLAIM_POLICY" != "Retain" ]; then
    echo "❌ PV reclaim policy is '$RECLAIM_POLICY' (should be 'Retain' for important data)"
    echo "💡 Hint: Change persistentVolumeReclaimPolicy to 'Retain' to preserve data"
    echo "💡 Retain = Data kept when PVC deleted (manual cleanup required)"
    echo "💡 Delete = Data automatically deleted when PVC deleted (data loss!)"
    exit 1
fi
echo "✅ PV has Retain reclaim policy (data will be preserved)"

echo ""
echo "🔍 Stage 3: Checking if PVC exists and is Bound..."
PVC_STATUS=$(kubectl get pvc "$PVC_NAME" -n "$NAMESPACE" -o jsonpath='{.status.phase}' 2>/dev/null)
if [ "$PVC_STATUS" != "Bound" ]; then
    echo "❌ PVC is not Bound (current: $PVC_STATUS)"
    exit 1
fi
echo "✅ PVC is Bound"

echo ""
echo "🔍 Stage 4: Verifying PVC is bound to the correct PV..."
BOUND_PV=$(kubectl get pvc "$PVC_NAME" -n "$NAMESPACE" -o jsonpath='{.spec.volumeName}')
if [ "$BOUND_PV" != "$PV_NAME" ]; then
    echo "❌ PVC is bound to wrong PV: $BOUND_PV (expected: $PV_NAME)"
    exit 1
fi
echo "✅ PVC correctly bound to PV with Retain policy"

echo ""
echo "🔍 Stage 5: Checking if pod exists..."
if ! kubectl get pod "$POD_NAME" -n "$NAMESPACE" &>/dev/null; then
    echo "❌ Pod '$POD_NAME' not found"
    exit 1
fi
echo "✅ Pod exists"

echo ""
echo "🔍 Stage 6: Checking if pod is Running..."
POD_STATUS=$(kubectl get pod "$POD_NAME" -n "$NAMESPACE" -o jsonpath='{.status.phase}')
if [ "$POD_STATUS" != "Running" ]; then
    echo "❌ Pod is in '$POD_STATUS' state (expected Running)"
    exit 1
fi
echo "✅ Pod is Running"

echo ""
echo "🔍 Stage 7: Verifying data was written..."
if ! kubectl logs "$POD_NAME" -n "$NAMESPACE" 2>/dev/null | grep -q "Data written successfully"; then
    echo "❌ Data not written successfully"
    exit 1
fi
echo "✅ Data written to volume"

echo ""
echo "🔍 Stage 8: Testing data persistence guarantee..."
DATA_CONTENT=$(kubectl exec "$POD_NAME" -n "$NAMESPACE" -- cat /data/important.txt 2>/dev/null)
if [ -z "$DATA_CONTENT" ]; then
    echo "❌ Cannot read data from volume"
    exit 1
fi
echo "✅ Data is accessible and will be retained even if PVC is deleted"

echo ""
echo "🎉 SUCCESS! PV configured with Retain policy - data is safe from accidental deletion!"
echo ""
echo "📝 Note: With Retain policy, when PVC is deleted:"
echo "   - PV status changes to 'Released'"
echo "   - Data remains on disk"
echo "   - Manual cleanup required before PV can be reused"
