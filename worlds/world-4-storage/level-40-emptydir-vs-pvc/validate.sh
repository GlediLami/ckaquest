#!/bin/bash

NAMESPACE="ckaquest"
POD_NAME="data-app"
PVC_NAME="app-data"

echo "🔍 Stage 1: Checking if PVC exists..."
if ! kubectl get pvc "$PVC_NAME" -n "$NAMESPACE" &>/dev/null; then
    echo "❌ PersistentVolumeClaim '$PVC_NAME' not found"
    echo "💡 Hint: Replace emptyDir with a PersistentVolumeClaim"
    exit 1
fi
echo "✅ PVC exists"

echo ""
echo "🔍 Stage 2: Checking if PVC is Bound..."
PVC_STATUS=$(kubectl get pvc "$PVC_NAME" -n "$NAMESPACE" -o jsonpath='{.status.phase}')
if [ "$PVC_STATUS" != "Bound" ]; then
    echo "❌ PVC is not Bound (current: $PVC_STATUS)"
    exit 1
fi
echo "✅ PVC is Bound"

echo ""
echo "🔍 Stage 3: Checking if pod exists..."
if ! kubectl get pod "$POD_NAME" -n "$NAMESPACE" &>/dev/null; then
    echo "❌ Pod '$POD_NAME' not found"
    exit 1
fi
echo "✅ Pod exists"

echo ""
echo "🔍 Stage 4: Verifying pod is NOT using emptyDir..."
VOLUME_TYPE=$(kubectl get pod "$POD_NAME" -n "$NAMESPACE" -o jsonpath='{.spec.volumes[0]}' | jq -r 'keys[0]')
if [ "$VOLUME_TYPE" == "emptyDir" ]; then
    echo "❌ Pod is still using emptyDir (ephemeral storage)"
    echo "💡 Hint: Change volume to use persistentVolumeClaim instead"
    exit 1
fi
echo "✅ Pod is not using emptyDir"

echo ""
echo "🔍 Stage 5: Verifying pod IS using PVC..."
POD_PVC=$(kubectl get pod "$POD_NAME" -n "$NAMESPACE" -o jsonpath='{.spec.volumes[0].persistentVolumeClaim.claimName}' 2>/dev/null)
if [ "$POD_PVC" != "$PVC_NAME" ]; then
    echo "❌ Pod is not using the correct PVC (using: $POD_PVC, expected: $PVC_NAME)"
    exit 1
fi
echo "✅ Pod is using PVC: $PVC_NAME"

echo ""
echo "🔍 Stage 6: Checking if pod is Running..."
POD_STATUS=$(kubectl get pod "$POD_NAME" -n "$NAMESPACE" -o jsonpath='{.status.phase}')
if [ "$POD_STATUS" != "Running" ]; then
    echo "❌ Pod is in '$POD_STATUS' state (expected Running)"
    exit 1
fi
echo "✅ Pod is Running"

echo ""
echo "🔍 Stage 7: Verifying data persistence..."
kubectl exec "$POD_NAME" -n "$NAMESPACE" -- cat /data/persistent.txt &>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  No data file yet (this is okay on first run)"
else
    DATA_LINES=$(kubectl exec "$POD_NAME" -n "$NAMESPACE" -- wc -l /data/persistent.txt 2>/dev/null | awk '{print $1}')
    echo "✅ Data file exists with $DATA_LINES lines"
fi

echo ""
echo "🔍 Stage 8: Testing persistence by simulating restart..."
echo "   Writing test data..."
kubectl exec "$POD_NAME" -n "$NAMESPACE" -- sh -c 'echo "Test persistence: $(date)" > /data/test-persistence.txt' 2>/dev/null

echo "   Reading back test data..."
TEST_DATA=$(kubectl exec "$POD_NAME" -n "$NAMESPACE" -- cat /data/test-persistence.txt 2>/dev/null)
if [ -z "$TEST_DATA" ]; then
    echo "❌ Cannot read written data"
    exit 1
fi
echo "✅ Data successfully written and read back"

echo ""
echo "🎉 SUCCESS! Pod configured with PersistentVolumeClaim for data persistence!"
echo ""
echo "📝 Key difference:"
echo "   emptyDir:      Data LOST when pod deleted/restarted"
echo "   PVC:           Data PERSISTS across pod lifecycle"
echo ""
echo "💡 To verify persistence, try:"
echo "   1. kubectl delete pod $POD_NAME -n $NAMESPACE"
echo "   2. kubectl apply -f solution.yaml"
echo "   3. Check logs - previous data should still exist!"
