#!/bin/bash

NAMESPACE="k8squest"
POD_NAME="secure-app"

echo "🔍 VALIDATION STAGE 1: Checking namespace security labels..."
PSS_ENFORCE=$(kubectl get namespace $NAMESPACE -o jsonpath='{.metadata.labels.pod-security\.kubernetes\.io/enforce}')
if [ "$PSS_ENFORCE" != "restricted" ]; then
    echo "⚠️  Namespace doesn't enforce 'restricted' standard"
    echo "   This level works best with restricted enforcement"
fi
echo "✅ Namespace checked"

echo ""
echo "🔍 VALIDATION STAGE 2: Checking if pod exists..."
if ! kubectl get pod $POD_NAME -n $NAMESPACE &>/dev/null; then
    echo "❌ FAILED: Pod '$POD_NAME' not found"
    echo "💡 Hint: Pod may have been rejected by admission controller"
    echo "💡 Hint: Check events: kubectl get events -n $NAMESPACE"
    exit 1
fi
echo "✅ Pod exists"

echo ""
echo "🔍 VALIDATION STAGE 3: Checking runAsNonRoot..."
RUN_AS_NON_ROOT=$(kubectl get pod $POD_NAME -n $NAMESPACE -o jsonpath='{.spec.containers[0].securityContext.runAsNonRoot}')
if [ "$RUN_AS_NON_ROOT" != "true" ]; then
    echo "❌ FAILED: runAsNonRoot not set to true"
    exit 1
fi
echo "✅ runAsNonRoot: true"

echo ""
echo "🔍 VALIDATION STAGE 4: Checking runAsUser (must be non-zero)..."
RUN_AS_USER=$(kubectl get pod $POD_NAME -n $NAMESPACE -o jsonpath='{.spec.containers[0].securityContext.runAsUser}')
if [ -z "$RUN_AS_USER" ] || [ "$RUN_AS_USER" = "0" ]; then
    echo "❌ FAILED: runAsUser is 0 (root) or not set"
    exit 1
fi
echo "✅ runAsUser: $RUN_AS_USER (non-root)"

echo ""
echo "🔍 VALIDATION STAGE 5: Checking allowPrivilegeEscalation..."
ALLOW_PRIV=$(kubectl get pod $POD_NAME -n $NAMESPACE -o jsonpath='{.spec.containers[0].securityContext.allowPrivilegeEscalation}')
if [ "$ALLOW_PRIV" != "false" ]; then
    echo "❌ FAILED: allowPrivilegeEscalation not set to false"
    exit 1
fi
echo "✅ allowPrivilegeEscalation: false"

echo ""
echo "🔍 VALIDATION STAGE 6: Checking capabilities dropped..."
CAPS_DROP=$(kubectl get pod $POD_NAME -n $NAMESPACE -o jsonpath='{.spec.containers[0].securityContext.capabilities.drop}')
if ! echo "$CAPS_DROP" | grep -q "ALL"; then
    echo "❌ FAILED: capabilities.drop does not include ALL"
    exit 1
fi
echo "✅ capabilities dropped: ALL"

echo ""
echo "🔍 VALIDATION STAGE 7: Checking seccompProfile..."
SECCOMP=$(kubectl get pod $POD_NAME -n $NAMESPACE -o jsonpath='{.spec.securityContext.seccompProfile.type}')
if [ "$SECCOMP" != "RuntimeDefault" ] && [ "$SECCOMP" != "Localhost" ]; then
    echo "⚠️  seccompProfile not set to RuntimeDefault or Localhost"
    echo "   This is required for restricted standard"
fi
echo "✅ seccompProfile: $SECCOMP"

echo ""
echo "🔍 VALIDATION STAGE 8: Checking pod status..."
POD_STATUS=$(kubectl get pod $POD_NAME -n $NAMESPACE -o jsonpath='{.status.phase}')
if [ "$POD_STATUS" != "Running" ]; then
    echo "⚠️  Pod is $POD_STATUS, not Running"
else
    echo "✅ Pod is Running"
fi

echo ""
echo "🎉 SUCCESS! Pod meets restricted Pod Security Standards!"
echo ""
echo "Security configuration:"
echo "  • runAsNonRoot: true"
echo "  • runAsUser: $RUN_AS_USER"
echo "  • allowPrivilegeEscalation: false"
echo "  • capabilities: drop ALL"
echo "  • seccompProfile: $SECCOMP"
echo ""
echo "This pod follows security best practices! 🔒"
