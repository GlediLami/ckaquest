#!/bin/bash

NAMESPACE="k8squest"
SECRET="db-credentials"
POD_NAME="database-client"

echo "🔍 Stage 1: Checking if Secret exists..."
if ! kubectl get secret "$SECRET" -n "$NAMESPACE" &>/dev/null; then
    echo "❌ Secret '$SECRET' not found"
    exit 1
fi
echo "✅ Secret exists"

echo ""
echo "🔍 Stage 2: Checking if username is base64 encoded..."
USERNAME_RAW=$(kubectl get secret "$SECRET" -n "$NAMESPACE" -o jsonpath='{.data.username}')
if [ -z "$USERNAME_RAW" ]; then
    echo "❌ username key not found in Secret data"
    exit 1
fi

# Try to decode - if it fails, it's not valid base64
USERNAME_DECODED=$(echo "$USERNAME_RAW" | base64 -d 2>/dev/null)
if [ $? -ne 0 ]; then
    echo "❌ username is not properly base64 encoded"
    echo "💡 Hint: Use 'echo -n \"value\" | base64' to encode"
    exit 1
fi
echo "✅ username is base64 encoded (decodes to: $USERNAME_DECODED)"

echo ""
echo "🔍 Stage 3: Checking if password is base64 encoded..."
PASSWORD_RAW=$(kubectl get secret "$SECRET" -n "$NAMESPACE" -o jsonpath='{.data.password}')
if [ -z "$PASSWORD_RAW" ]; then
    echo "❌ password key not found in Secret data"
    exit 1
fi

PASSWORD_DECODED=$(echo "$PASSWORD_RAW" | base64 -d 2>/dev/null)
if [ $? -ne 0 ]; then
    echo "❌ password is not properly base64 encoded"
    exit 1
fi
echo "✅ password is base64 encoded"

echo ""
echo "🔍 Stage 4: Checking if pod exists..."
if ! kubectl get pod "$POD_NAME" -n "$NAMESPACE" &>/dev/null; then
    echo "❌ Pod '$POD_NAME' not found"
    exit 1
fi
echo "✅ Pod exists"

echo ""
echo "🔍 Stage 5: Checking if pod is Running..."
POD_STATUS=$(kubectl get pod "$POD_NAME" -n "$NAMESPACE" -o jsonpath='{.status.phase}')
if [ "$POD_STATUS" != "Running" ]; then
    echo "❌ Pod is in '$POD_STATUS' state (expected Running)"
    exit 1
fi
echo "✅ Pod is Running"

echo ""
echo "🔍 Stage 6: Verifying credentials were properly decoded in pod..."
if ! kubectl logs "$POD_NAME" -n "$NAMESPACE" 2>/dev/null | grep -q "Connected successfully"; then
    echo "❌ Pod did not connect successfully"
    echo "💡 Check logs: kubectl logs $POD_NAME -n $NAMESPACE"
    exit 1
fi
echo "✅ Credentials properly decoded and used"

echo ""
echo "🔍 Stage 7: Validating secret values..."
POD_USERNAME=$(kubectl exec "$POD_NAME" -n "$NAMESPACE" -- sh -c 'echo $DB_USER' 2>/dev/null)
if [ "$POD_USERNAME" != "$USERNAME_DECODED" ]; then
    echo "❌ Pod received incorrect username"
    exit 1
fi
echo "✅ Secret values correctly decoded in pod"

echo ""
echo "🎉 SUCCESS! Secret properly base64 encoded and pod using credentials!"
