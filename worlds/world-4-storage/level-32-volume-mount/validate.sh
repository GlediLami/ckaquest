#!/bin/bash

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "🔍 Validating Level 32: Volume Mount Path Error..."
echo ""

echo "📋 Stage 1: Checking pod exists..."
if ! kubectl get pod web-app -n k8squest &>/dev/null; then
    echo -e "${RED}❌ Pod 'web-app' not found${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Pod exists${NC}"
echo ""

echo "📋 Stage 2: Checking pod status..."
sleep 5
POD_STATUS=$(kubectl get pod web-app -n k8squest -o jsonpath='{.status.phase}')

if [ "$POD_STATUS" != "Running" ]; then
    echo -e "${RED}❌ Pod is not running (status: $POD_STATUS)${NC}"
    echo ""
    echo "💡 Check pod logs:"
    echo "   kubectl logs web-app -n k8squest"
    echo ""
    echo "   If you see 'Config file not found', the volume is mounted at wrong path"
    exit 1
fi
echo -e "${GREEN}✓ Pod is running${NC}"
echo ""

echo "📋 Stage 3: Verifying volume mount path..."
MOUNT_PATH=$(kubectl get pod web-app -n k8squest -o jsonpath='{.spec.containers[0].volumeMounts[0].mountPath}')

if [ "$MOUNT_PATH" != "/app/config" ]; then
    echo -e "${RED}❌ Volume mounted at wrong path: $MOUNT_PATH${NC}"
    echo "   Expected: /app/config"
    echo ""
    echo "💡 Fix the mountPath in volumeMounts section"
    exit 1
fi
echo -e "${GREEN}✓ Volume mounted at /app/config${NC}"
echo ""

echo "📋 Stage 4: Verifying config file exists..."
if ! kubectl exec web-app -n k8squest -- test -f /app/config/app.conf 2>/dev/null; then
    echo -e "${RED}❌ Config file not found at /app/config/app.conf${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Config file exists at /app/config/app.conf${NC}"
echo ""

echo "📋 Stage 5: Verifying app can read config..."
CONFIG_CONTENT=$(kubectl exec web-app -n k8squest -- cat /app/config/app.conf 2>/dev/null)
if [ -z "$CONFIG_CONTENT" ]; then
    echo -e "${RED}❌ Cannot read config file${NC}"
    exit 1
fi
echo -e "${GREEN}✓ App can read config file${NC}"
echo "   Content: $CONFIG_CONTENT"
echo ""

echo "📋 Stage 6: Final validation..."
echo -e "${GREEN}✓ All checks passed!${NC}"
echo ""
echo "🎉 Success! Volume is mounted at the correct path"
echo ""
echo "📊 Configuration:"
echo "   • Mount Path: /app/config"
echo "   • Config File: app.conf"
echo "   • Pod Status: Running"
echo ""
echo "💡 Key Concept: mountPath determines WHERE in the container the volume appears"
echo ""

exit 0
