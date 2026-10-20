#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🔍 Validating Level 31: PersistentVolumeClaim Pending..."
echo ""

# Stage 1: Check if PVC exists
echo "📋 Stage 1: Checking if PVC exists..."
if ! kubectl get pvc app-storage-claim -n ckaquest &>/dev/null; then
    echo -e "${RED}❌ PVC 'app-storage-claim' not found in namespace 'ckaquest'${NC}"
    echo ""
    echo "💡 Make sure to apply your fixed configuration with the PVC definition."
    exit 1
fi
echo -e "${GREEN}✓ PVC exists${NC}"
echo ""

# Stage 2: Check PVC status
echo "📋 Stage 2: Checking PVC binding status..."
PVC_STATUS=$(kubectl get pvc app-storage-claim -n ckaquest -o jsonpath='{.status.phase}')

if [ "$PVC_STATUS" == "Pending" ]; then
    echo -e "${RED}❌ PVC is still in Pending state${NC}"
    echo ""
    echo "💡 PVC remains pending when:"
    echo "   1. No PersistentVolume matches the PVC requirements"
    echo "   2. Storage capacity doesn't match (PV too small)"
    echo "   3. StorageClass doesn't match"
    echo "   4. Access modes don't match"
    echo ""
    echo "🔍 Troubleshooting steps:"
    echo "   • Check PVC requirements:"
    echo "     kubectl describe pvc app-storage-claim -n ckaquest"
    echo ""
    echo "   • Look for available PVs:"
    echo "     kubectl get pv"
    echo ""
    echo "   • Check PVC events:"
    echo "     kubectl get events -n ckaquest | grep app-storage-claim"
    echo ""
    
    # Show what PVC is requesting
    REQUESTED_STORAGE=$(kubectl get pvc app-storage-claim -n ckaquest -o jsonpath='{.spec.resources.requests.storage}')
    REQUESTED_CLASS=$(kubectl get pvc app-storage-claim -n ckaquest -o jsonpath='{.spec.storageClassName}')
    REQUESTED_MODE=$(kubectl get pvc app-storage-claim -n ckaquest -o jsonpath='{.spec.accessModes[0]}')
    
    echo "📊 PVC Requirements:"
    echo "   • Storage: $REQUESTED_STORAGE"
    echo "   • StorageClass: $REQUESTED_CLASS"
    echo "   • AccessMode: $REQUESTED_MODE"
    echo ""
    
    # Check if PV exists and show its specs
    if kubectl get pv app-storage &>/dev/null; then
        PV_CAPACITY=$(kubectl get pv app-storage -o jsonpath='{.spec.capacity.storage}')
        PV_CLASS=$(kubectl get pv app-storage -o jsonpath='{.spec.storageClassName}')
        PV_MODE=$(kubectl get pv app-storage -o jsonpath='{.spec.accessModes[0]}')
        
        echo "📊 Available PV 'app-storage':"
        echo "   • Storage: $PV_CAPACITY"
        echo "   • StorageClass: $PV_CLASS"
        echo "   • AccessMode: $PV_MODE"
        echo ""
        
        # Check mismatches
        if [ "$PV_CAPACITY" != "$REQUESTED_STORAGE" ]; then
            echo -e "${YELLOW}⚠️  Storage mismatch: PV has $PV_CAPACITY, PVC needs $REQUESTED_STORAGE${NC}"
        fi
        if [ "$PV_CLASS" != "$REQUESTED_CLASS" ]; then
            echo -e "${YELLOW}⚠️  StorageClass mismatch: PV has '$PV_CLASS', PVC needs '$REQUESTED_CLASS'${NC}"
        fi
        if [ "$PV_MODE" != "$REQUESTED_MODE" ]; then
            echo -e "${YELLOW}⚠️  AccessMode mismatch: PV has $PV_MODE, PVC needs $REQUESTED_MODE${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  No PersistentVolume named 'app-storage' found${NC}"
        echo "   Create a PV that matches the PVC requirements above."
    fi
    echo ""
    echo "🔧 Fix the PV to match all PVC requirements!"
    exit 1
fi

if [ "$PVC_STATUS" != "Bound" ]; then
    echo -e "${RED}❌ PVC status is '$PVC_STATUS' (expected: Bound)${NC}"
    exit 1
fi

echo -e "${GREEN}✓ PVC is Bound${NC}"
echo ""

# Stage 3: Verify PV exists and is bound
echo "📋 Stage 3: Checking PersistentVolume..."
PV_NAME=$(kubectl get pvc app-storage-claim -n ckaquest -o jsonpath='{.spec.volumeName}')

if [ -z "$PV_NAME" ]; then
    echo -e "${RED}❌ PVC is not bound to any PV${NC}"
    exit 1
fi

if ! kubectl get pv "$PV_NAME" &>/dev/null; then
    echo -e "${RED}❌ PV '$PV_NAME' not found${NC}"
    exit 1
fi

PV_STATUS=$(kubectl get pv "$PV_NAME" -o jsonpath='{.status.phase}')
if [ "$PV_STATUS" != "Bound" ]; then
    echo -e "${RED}❌ PV status is '$PV_STATUS' (expected: Bound)${NC}"
    exit 1
fi

echo -e "${GREEN}✓ PV '$PV_NAME' is bound to PVC${NC}"
echo ""

# Stage 4: Check storage capacity match
echo "📋 Stage 4: Verifying storage capacity..."
PV_CAPACITY=$(kubectl get pv "$PV_NAME" -o jsonpath='{.spec.capacity.storage}')
PVC_REQUEST=$(kubectl get pvc app-storage-claim -n ckaquest -o jsonpath='{.spec.resources.requests.storage}')

echo "   PV capacity: $PV_CAPACITY"
echo "   PVC request: $PVC_REQUEST"

# Convert to bytes for comparison (simple check for common cases)
if [[ "$PV_CAPACITY" == *"Mi"* ]] && [[ "$PVC_REQUEST" == *"Gi"* ]]; then
    echo -e "${YELLOW}⚠️  Warning: PV capacity might be too small${NC}"
fi

echo -e "${GREEN}✓ Storage capacity validated${NC}"
echo ""

# Stage 5: Check pod status
echo "📋 Stage 5: Checking pod status..."
if ! kubectl get pod database-pod -n ckaquest &>/dev/null; then
    echo -e "${RED}❌ Pod 'database-pod' not found${NC}"
    exit 1
fi

# Wait a bit for pod to start
sleep 3

POD_STATUS=$(kubectl get pod database-pod -n ckaquest -o jsonpath='{.status.phase}')
if [ "$POD_STATUS" != "Running" ]; then
    echo -e "${RED}❌ Pod is not running (status: $POD_STATUS)${NC}"
    echo ""
    echo "💡 Check pod events:"
    echo "   kubectl describe pod database-pod -n ckaquest"
    exit 1
fi

echo -e "${GREEN}✓ Pod is running${NC}"
echo ""

# Stage 6: Verify volume is mounted
echo "📋 Stage 6: Verifying volume mount..."
MOUNT_CHECK=$(kubectl exec database-pod -n ckaquest -- ls /data 2>&1)
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Volume not properly mounted at /data${NC}"
    echo "   Error: $MOUNT_CHECK"
    exit 1
fi

echo -e "${GREEN}✓ Volume mounted successfully at /data${NC}"
echo ""

# Stage 7: Final validation
echo "📋 Stage 7: Final validation..."
echo -e "${GREEN}✓ All checks passed!${NC}"
echo ""
echo "🎉 Success! Your PVC is now bound and the pod is using persistent storage"
echo ""
echo "📊 Storage Details:"
echo "   • PVC: app-storage-claim (Bound)"
echo "   • PV: $PV_NAME (Bound)"
echo "   • Capacity: $PV_CAPACITY"
echo "   • Pod: database-pod (Running)"
echo "   • Mount: /data"
echo ""
echo "💡 Key Concepts:"
echo "   • PVC requests storage, PV provides it"
echo "   • They must match: capacity, storage class, access mode"
echo "   • PVC stays Pending until a matching PV is available"
echo "   • Pod can't start until PVC is Bound"
echo ""

exit 0
