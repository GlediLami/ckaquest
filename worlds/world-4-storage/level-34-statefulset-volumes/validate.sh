#!/bin/bash

NAMESPACE="ckaquest"
STATEFULSET="postgres-cluster"

echo "🔍 Stage 1: Checking if StatefulSet exists..."
if ! kubectl get statefulset "$STATEFULSET" -n "$NAMESPACE" &>/dev/null; then
    echo "❌ StatefulSet '$STATEFULSET' not found"
    exit 1
fi
echo "✅ StatefulSet exists"

echo ""
echo "🔍 Stage 2: Checking if volumeClaimTemplates is configured..."
VOLUME_CLAIM_TEMPLATES=$(kubectl get statefulset "$STATEFULSET" -n "$NAMESPACE" -o jsonpath='{.spec.volumeClaimTemplates}')
if [ "$VOLUME_CLAIM_TEMPLATES" == "null" ] || [ -z "$VOLUME_CLAIM_TEMPLATES" ]; then
    echo "❌ volumeClaimTemplates is not configured in StatefulSet"
    echo "💡 Hint: StatefulSets should use volumeClaimTemplates for per-pod storage"
    exit 1
fi
echo "✅ volumeClaimTemplates is configured"

echo ""
echo "🔍 Stage 3: Checking if 3 pods are ready..."
READY_PODS=$(kubectl get statefulset "$STATEFULSET" -n "$NAMESPACE" -o jsonpath='{.status.readyReplicas}' 2>/dev/null)
if [ "$READY_PODS" != "3" ]; then
    echo "❌ Only $READY_PODS out of 3 pods are ready"
    echo "💡 Check: kubectl get pods -n $NAMESPACE -l app=postgres"
    exit 1
fi
echo "✅ All 3 pods are ready"

echo ""
echo "🔍 Stage 4: Checking if each pod has its own PVC..."
PVC_COUNT=$(kubectl get pvc -n "$NAMESPACE" -l app=postgres 2>/dev/null | grep -c "database-storage")
if [ "$PVC_COUNT" -lt "3" ]; then
    echo "❌ Found only $PVC_COUNT PVCs (expected 3, one per pod)"
    echo "💡 Each StatefulSet pod should have its own PVC"
    exit 1
fi
echo "✅ Found $PVC_COUNT PVCs (one per pod)"

echo ""
echo "🔍 Stage 5: Verifying PVC naming pattern..."
# StatefulSet PVCs should follow pattern: <template-name>-<statefulset-name>-<ordinal>
if ! kubectl get pvc -n "$NAMESPACE" | grep -q "database-storage-postgres-cluster-0"; then
    echo "❌ PVCs don't follow StatefulSet naming pattern"
    echo "💡 Expected: database-storage-postgres-cluster-0, database-storage-postgres-cluster-1, etc."
    exit 1
fi
echo "✅ PVCs follow correct naming pattern"

echo ""
echo "🔍 Stage 6: Checking if all PVCs are Bound..."
UNBOUND_PVCS=$(kubectl get pvc -n "$NAMESPACE" -l app=postgres -o jsonpath='{.items[?(@.status.phase!="Bound")].metadata.name}')
if [ -n "$UNBOUND_PVCS" ]; then
    echo "❌ Some PVCs are not Bound: $UNBOUND_PVCS"
    exit 1
fi
echo "✅ All PVCs are Bound"

echo ""
echo "🔍 Stage 7: Verifying pod-to-PVC mapping..."
for i in 0 1 2; do
    POD_NAME="postgres-cluster-$i"
    EXPECTED_PVC="database-storage-postgres-cluster-$i"
    ACTUAL_PVC=$(kubectl get pod "$POD_NAME" -n "$NAMESPACE" -o jsonpath='{.spec.volumes[?(@.name=="database-storage")].persistentVolumeClaim.claimName}' 2>/dev/null)
    
    if [ "$ACTUAL_PVC" != "$EXPECTED_PVC" ]; then
        echo "❌ Pod $POD_NAME is using PVC '$ACTUAL_PVC' instead of '$EXPECTED_PVC'"
        exit 1
    fi
done
echo "✅ Each pod is correctly mapped to its own PVC"

echo ""
echo "🎉 SUCCESS! StatefulSet configured with per-pod persistent storage!"
