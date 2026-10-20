#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🔍 Validating Level 29: LoadBalancer vs NodePort..."
echo ""

# Stage 1: Check if service exists
echo "📋 Stage 1: Checking if service exists..."
if ! kubectl get service web-service -n k8squest &>/dev/null; then
    echo -e "${RED}❌ Service 'web-service' not found in namespace 'k8squest'${NC}"
    echo ""
    echo "💡 The service might have been deleted. Make sure to apply your fixed configuration."
    exit 1
fi
echo -e "${GREEN}✓ Service exists${NC}"
echo ""

# Stage 2: Check service type
echo "📋 Stage 2: Checking service type..."
SERVICE_TYPE=$(kubectl get service web-service -n k8squest -o jsonpath='{.spec.type}')

if [ "$SERVICE_TYPE" == "LoadBalancer" ]; then
    echo -e "${RED}❌ Service is still type LoadBalancer${NC}"
    echo ""
    echo "💡 Problem: LoadBalancer services require cloud provider integration"
    echo "   In local clusters (kind, minikube, k3d), LoadBalancer services stay in 'Pending' state"
    echo ""
    echo "📚 Service types in Kubernetes:"
    echo "   • ClusterIP (default): Only accessible within cluster"
    echo "   • NodePort: Accessible via <NodeIP>:<NodePort> (works in local clusters)"
    echo "   • LoadBalancer: Provisions external LB (needs cloud provider like AWS, GCP, Azure)"
    echo ""
    echo "🔧 For local development, change the service type to NodePort"
    exit 1
fi

if [ "$SERVICE_TYPE" != "NodePort" ]; then
    echo -e "${RED}❌ Service type is '$SERVICE_TYPE' (expected: NodePort)${NC}"
    echo ""
    echo "💡 For local cluster access, use type: NodePort"
    exit 1
fi
echo -e "${GREEN}✓ Service type is NodePort${NC}"
echo ""

# Stage 3: Check if service has external access
echo "📋 Stage 3: Checking service accessibility..."

# Get node port
NODE_PORT=$(kubectl get service web-service -n k8squest -o jsonpath='{.spec.ports[0].nodePort}')
if [ -z "$NODE_PORT" ]; then
    echo -e "${RED}❌ No nodePort assigned to service${NC}"
    echo ""
    echo "💡 NodePort should be automatically assigned (or you can specify one)"
    exit 1
fi

echo -e "${GREEN}✓ NodePort assigned: $NODE_PORT${NC}"
echo ""

# Stage 4: Verify pod is running
echo "📋 Stage 4: Checking if backend pod is running..."
if ! kubectl get pod web-app -n k8squest &>/dev/null; then
    echo -e "${RED}❌ Pod 'web-app' not found${NC}"
    exit 1
fi

POD_STATUS=$(kubectl get pod web-app -n k8squest -o jsonpath='{.status.phase}')
if [ "$POD_STATUS" != "Running" ]; then
    echo -e "${RED}❌ Pod is not running (status: $POD_STATUS)${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Backend pod is running${NC}"
echo ""

# Stage 5: Check service endpoints
echo "📋 Stage 5: Verifying service endpoints..."
ENDPOINTS=$(kubectl get endpoints web-service -n k8squest -o jsonpath='{.subsets[*].addresses[*].ip}')
if [ -z "$ENDPOINTS" ]; then
    echo -e "${RED}❌ Service has no endpoints${NC}"
    echo ""
    echo "💡 Check if:"
    echo "   • Pod labels match service selector"
    echo "   • Pod is in Ready state"
    exit 1
fi
echo -e "${GREEN}✓ Service has endpoints: $ENDPOINTS${NC}"
echo ""

# Stage 6: Final validation
echo "📋 Stage 6: Final validation..."
echo -e "${GREEN}✓ All checks passed!${NC}"
echo ""
echo "🎉 Success! Your service is now accessible via NodePort"
echo ""
echo "📊 Service Details:"
echo "   • Type: NodePort"
echo "   • Port: 80"
echo "   • NodePort: $NODE_PORT"
echo ""
echo "🔗 Access the service:"
echo "   From within cluster: http://web-service.k8squest.svc.cluster.local"
echo "   From your machine: http://localhost:$NODE_PORT (if port-forwarded)"
echo "   Via kubectl: kubectl port-forward -n k8squest service/web-service 8080:80"
echo ""
echo "💡 NodePort vs LoadBalancer:"
echo "   • NodePort: Exposes service on static port on each node (works everywhere)"
echo "   • LoadBalancer: Provisions external LB (needs cloud provider integration)"
echo ""

exit 0
