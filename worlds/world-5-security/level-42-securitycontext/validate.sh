#!/bin/bash

NAMESPACE="k8squest"
POD_NAME="web-app"

echo "🔍 VALIDATION STAGE 1: Checking if pod exists..."
if ! kubectl get pod $POD_NAME -n $NAMESPACE &>/dev/null; then
    echo "❌ FAILED: Pod '$POD_NAME' not found in namespace '$NAMESPACE'"
    exit 1
fi
echo "✅ Pod exists"

echo ""
echo "🔍 VALIDATION STAGE 2: Checking if pod is running..."
POD_STATUS=$(kubectl get pod $POD_NAME -n $NAMESPACE -o jsonpath='{.status.phase}')
if [ "$POD_STATUS" != "Running" ]; then
    echo "❌ FAILED: Pod is in '$POD_STATUS' state, not Running"
    echo "💡 Hint: Check pod events with: kubectl describe pod $POD_NAME -n $NAMESPACE"
    exit 1
fi
echo "✅ Pod is running"

echo ""
echo "🔍 VALIDATION STAGE 3: Verifying runAsNonRoot is enabled..."
RUN_AS_NON_ROOT=$(kubectl get pod $POD_NAME -n $NAMESPACE -o jsonpath='{.spec.containers[0].securityContext.runAsNonRoot}')
if [ "$RUN_AS_NON_ROOT" != "true" ]; then
    echo "❌ FAILED: runAsNonRoot is not set to true"
    echo "💡 Hint: Add 'runAsNonRoot: true' in securityContext"
    exit 1
fi
echo "✅ runAsNonRoot enabled"

echo ""
echo "🔍 VALIDATION STAGE 4: Verifying runAsUser is set to non-root..."
RUN_AS_USER=$(kubectl get pod $POD_NAME -n $NAMESPACE -o jsonpath='{.spec.containers[0].securityContext.runAsUser}')
if [ -z "$RUN_AS_USER" ] || [ "$RUN_AS_USER" = "0" ]; then
    echo "❌ FAILED: runAsUser not set or set to root (0)"
    echo "💡 Hint: Add 'runAsUser: 1000' (or any non-zero UID) in securityContext"
    exit 1
fi
echo "✅ runAsUser set to $RUN_AS_USER (non-root)"

echo ""
echo "🔍 VALIDATION STAGE 5: Verifying privilege escalation is disabled..."
ALLOW_PRIV_ESC=$(kubectl get pod $POD_NAME -n $NAMESPACE -o jsonpath='{.spec.containers[0].securityContext.allowPrivilegeEscalation}')
if [ "$ALLOW_PRIV_ESC" != "false" ]; then
    echo "❌ FAILED: allowPrivilegeEscalation is not set to false"
    echo "💡 Hint: Add 'allowPrivilegeEscalation: false' in securityContext"
    exit 1
fi
echo "✅ Privilege escalation disabled"

echo ""
echo "🔍 VALIDATION STAGE 6: Verifying container is actually running as non-root..."
ACTUAL_USER=$(kubectl exec $POD_NAME -n $NAMESPACE -- id -u 2>/dev/null || echo "0")
if [ "$ACTUAL_USER" = "0" ]; then
    echo "❌ FAILED: Container is running as root (UID 0)"
    echo "💡 Hint: Container user doesn't match runAsUser setting"
    exit 1
fi
echo "✅ Container running as UID $ACTUAL_USER (non-root)"

echo ""
echo "🎉 SUCCESS! All security validations passed!"
echo "Your container is now running securely:"
echo "  - As non-root user (UID $RUN_AS_USER)"
echo "  - With privilege escalation disabled"
echo "  - Meeting security best practices"
