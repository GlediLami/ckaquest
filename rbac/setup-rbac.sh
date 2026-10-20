#!/bin/bash
set -e

echo "🛡️  Setting up K8sQuest Safety Guards"
echo "======================================"
echo ""

# Check if k8squest namespace exists
if ! kubectl get namespace k8squest >/dev/null 2>&1; then
  echo "Creating k8squest namespace..."
  kubectl create namespace k8squest
fi

# Apply RBAC configuration
echo "Applying RBAC policies..."
kubectl apply -f rbac/k8squest-rbac.yaml

echo ""
echo "✅ RBAC Setup Complete!"
echo ""
echo "📋 What was configured:"
echo "  • ServiceAccount: k8squest-player"
echo "  • Role: Full access within k8squest namespace"
echo "  • ClusterRole: Read-only cluster-wide access"
echo ""
echo "🔒 Safety Features:"
echo "  ✓ Cannot modify resources outside k8squest namespace"
echo "  ✓ Cannot delete nodes or critical namespaces"
echo "  ✓ Cannot modify cluster-level resources"
echo "  ✓ Read-only access to cluster info (nodes, storage classes)"
echo ""
echo "💡 To use this ServiceAccount:"
echo "   kubectl --as=system:serviceaccount:k8squest:k8squest-player <command>"
echo ""
echo "Or configure your context to use it by default."
echo ""
