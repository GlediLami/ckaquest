#!/bin/bash

NAMESPACE="ckaquest"
PVC_NAME="app-storage"
POD_NAME="data-processor"

echo "🔍 Stage 1: Checking if PVC exists..."
if ! kubectl get pvc "$PVC_NAME" -n "$NAMESPACE" &>/dev/null; then
    echo "❌ PVC '$PVC_NAME' not found"
    exit 1
fi
echo "✅ PVC exists"

echo ""
echo "🔍 Stage 2: Checking PVC's StorageClass..."
STORAGE_CLASS=$(kubectl get pvc "$PVC_NAME" -n "$NAMESPACE" -o jsonpath='{.spec.storageClassName}')
if [ -z "$STORAGE_CLASS" ]; then
    echo "❌ No StorageClass specified in PVC"
    exit 1
fi
echo "✅ PVC references StorageClass: $STORAGE_CLASS"

echo ""
echo "🔍 Stage 3: Verifying StorageClass exists..."
if ! kubectl get storageclass "$STORAGE_CLASS" &>/dev/null; then
    echo "❌ StorageClass '$STORAGE_CLASS' does not exist"
    echo "💡 Available StorageClasses:"
    kubectl get storageclass
    echo ""
    echo "💡 Hint: Update PVC to use an existing StorageClass"
    exit 1
fi
echo "✅ StorageClass '$STORAGE_CLASS' exists"

echo ""
echo "🔍 Stage 4: Checking if PVC is Bound..."
PVC_STATUS=$(kubectl get pvc "$PVC_NAME" -n "$NAMESPACE" -o jsonpath='{.status.phase}')
if [ "$PVC_STATUS" != "Bound" ]; then
    echo "❌ PVC is in '$PVC_STATUS' state (expected Bound)"
    echo "💡 Describe PVC to see why: kubectl describe pvc $PVC_NAME -n $NAMESPACE"
    exit 1
fi
echo "✅ PVC is Bound"

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
echo "🔍 Stage 7: Verifying volume is mounted..."
MOUNT_CHECK=$(kubectl exec "$POD_NAME" -n "$NAMESPACE" -- sh -c 'test -d /data && echo "mounted"' 2>/dev/null)
if [ "$MOUNT_CHECK" != "mounted" ]; then
    echo "❌ Volume not properly mounted at /data"
    exit 1
fi
echo "✅ Volume successfully mounted"

echo ""
echo "🎉 SUCCESS! PVC bound with valid StorageClass and pod running!"
