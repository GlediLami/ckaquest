#!/bin/bash

NAMESPACE="k8squest"
DEPLOYMENT="web-app"
PDB_NAME="web-pdb"

echo "🔍 VALIDATION STAGE 1: Checking if deployment exists..."
if ! kubectl get deployment $DEPLOYMENT -n $NAMESPACE &>/dev/null; then
    echo "❌ FAILED: Deployment '$DEPLOYMENT' not found"
    exit 1
fi
echo "✅ Deployment exists"

echo ""
echo "🔍 VALIDATION STAGE 2: Checking if PodDisruptionBudget exists..."
if ! kubectl get pdb $PDB_NAME -n $NAMESPACE &>/dev/null; then
    echo "❌ FAILED: PodDisruptionBudget '$PDB_NAME' not found"
    exit 1
fi
echo "✅ PodDisruptionBudget exists"

echo ""
echo "🔍 VALIDATION STAGE 3: Checking deployment replica count..."
REPLICAS=$(kubectl get deployment $DEPLOYMENT -n $NAMESPACE -o jsonpath='{.spec.replicas}')
if [ "$REPLICAS" -lt 2 ]; then
    echo "❌ FAILED: Deployment has $REPLICAS replica(s), need at least 2"
    exit 1
fi
echo "✅ Deployment has $REPLICAS replicas"

echo ""
echo "🔍 VALIDATION STAGE 4: Verifying PDB configuration..."
MIN_AVAILABLE=$(kubectl get pdb $PDB_NAME -n $NAMESPACE -o jsonpath='{.spec.minAvailable}')
MAX_UNAVAILABLE=$(kubectl get pdb $PDB_NAME -n $NAMESPACE -o jsonpath='{.spec.maxUnavailable}')

if [ -n "$MIN_AVAILABLE" ]; then
    echo "PDB minAvailable: $MIN_AVAILABLE"
    if [ "$MIN_AVAILABLE" -gt "$REPLICAS" ]; then
        echo "❌ FAILED: minAvailable ($MIN_AVAILABLE) > replicas ($REPLICAS)"
        echo "💡 Hint: minAvailable must be ≤ replicas"
        exit 1
    fi
elif [ -n "$MAX_UNAVAILABLE" ]; then
    echo "PDB maxUnavailable: $MAX_UNAVAILABLE"
else
    echo "❌ FAILED: PDB has neither minAvailable nor maxUnavailable"
    exit 1
fi
echo "✅ PDB configuration is valid"

echo ""
echo "🔍 VALIDATION STAGE 5: Checking PDB status..."
ALLOWED_DISRUPTIONS=$(kubectl get pdb $PDB_NAME -n $NAMESPACE -o jsonpath='{.status.disruptionsAllowed}')
if [ -z "$ALLOWED_DISRUPTIONS" ]; then
    echo "⚠️  PDB status not yet available (pods may still be starting)"
    sleep 5
    ALLOWED_DISRUPTIONS=$(kubectl get pdb $PDB_NAME -n $NAMESPACE -o jsonpath='{.status.disruptionsAllowed}')
fi

if [ "$ALLOWED_DISRUPTIONS" = "0" ]; then
    echo "⚠️  WARNING: No disruptions allowed (disruptionsAllowed: 0)"
    echo "   This means node drain would be blocked"
    echo "💡 Hint: Increase replicas or reduce minAvailable"
else
    echo "✅ Disruptions allowed: $ALLOWED_DISRUPTIONS"
fi

echo ""
echo "🔍 VALIDATION STAGE 6: Verifying pods are running..."
READY_REPLICAS=$(kubectl get deployment $DEPLOYMENT -n $NAMESPACE -o jsonpath='{.status.readyReplicas}')
if [ "$READY_REPLICAS" != "$REPLICAS" ]; then
    echo "⚠️  Only $READY_REPLICAS/$REPLICAS pods ready"
else
    echo "✅ All $REPLICAS pods are ready"
fi

echo ""
echo "🎉 SUCCESS! PodDisruptionBudget configured correctly!"
echo ""
echo "PDB Status:"
kubectl get pdb $PDB_NAME -n $NAMESPACE
echo ""
echo "Configuration allows $ALLOWED_DISRUPTIONS voluntary disruption(s)"
echo "This enables node maintenance while maintaining availability!"
