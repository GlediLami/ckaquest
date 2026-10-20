#!/bin/bash
# Level 11 Setup Script - Creates rollback history
# This ensures there's a previous revision to rollback to

echo "🔧 Setting up Level 11: Rollback scenario..."
echo ""

# Step 1: Deploy working version (revision 1)
echo "📦 Deploying initial working version (revision 1)..."
kubectl apply -f setup.yaml

# Wait for deployment to be ready (increased timeout)
echo "⏳ Waiting for initial deployment to stabilize..."
kubectl rollout status deployment/web-app -n k8squest --timeout=120s

if [ $? -ne 0 ]; then
    echo "⚠️  Initial deployment taking longer than expected, but continuing..."
fi

echo "✅ Revision 1 deployed"
echo ""

# Step 2: Update to broken version (revision 2)
echo "📦 Updating to broken version (revision 2)..."
kubectl apply -f broken.yaml

# Wait a moment for the update to start
sleep 5

echo ""
echo "✅ Level 11 setup complete!"
echo ""
echo "📊 Rollback history:"
kubectl rollout history deployment/web-app -n k8squest
echo ""
echo "🎯 Your mission: The deployment is stuck on a bad update."
echo "   Use 'kubectl rollout undo' to rollback to the working version!"
