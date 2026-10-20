#!/bin/bash

NAMESPACE="k8squest"
CONFIGMAP="app-config"
POD_NAME="web-app"

echo "🔍 Stage 1: Checking if ConfigMap exists..."
if ! kubectl get configmap "$CONFIGMAP" -n "$NAMESPACE" &>/dev/null; then
    echo "❌ ConfigMap '$CONFIGMAP' not found"
    exit 1
fi
echo "✅ ConfigMap exists"

echo ""
echo "🔍 Stage 2: Checking if database_host key exists in ConfigMap..."
DB_HOST=$(kubectl get configmap "$CONFIGMAP" -n "$NAMESPACE" -o jsonpath='{.data.database_host}' 2>/dev/null)
if [ -z "$DB_HOST" ]; then
    echo "❌ Key 'database_host' not found in ConfigMap"
    echo "💡 Hint: Add database_host key to ConfigMap data"
    echo "💡 Current keys:"
    kubectl get configmap "$CONFIGMAP" -n "$NAMESPACE" -o jsonpath='{.data}' | jq 'keys'
    exit 1
fi
echo "✅ database_host key exists: $DB_HOST"

echo ""
echo "🔍 Stage 3: Checking if pod exists..."
if ! kubectl get pod "$POD_NAME" -n "$NAMESPACE" &>/dev/null; then
    echo "❌ Pod '$POD_NAME' not found"
    exit 1
fi
echo "✅ Pod exists"

echo ""
echo "🔍 Stage 4: Checking if pod is Running..."
POD_STATUS=$(kubectl get pod "$POD_NAME" -n "$NAMESPACE" -o jsonpath='{.status.phase}')
if [ "$POD_STATUS" != "Running" ]; then
    echo "❌ Pod is in '$POD_STATUS' state (expected Running)"
    echo "💡 Check pod events: kubectl describe pod $POD_NAME -n $NAMESPACE"
    exit 1
fi
echo "✅ Pod is Running"

echo ""
echo "🔍 Stage 5: Verifying DATABASE_HOST environment variable..."
ENV_DB_HOST=$(kubectl exec "$POD_NAME" -n "$NAMESPACE" -- sh -c 'echo $DATABASE_HOST' 2>/dev/null)
if [ -z "$ENV_DB_HOST" ]; then
    echo "❌ DATABASE_HOST environment variable is not set in pod"
    exit 1
fi
echo "✅ DATABASE_HOST is set: $ENV_DB_HOST"

echo ""
echo "🔍 Stage 6: Checking pod logs for success message..."
if ! kubectl logs "$POD_NAME" -n "$NAMESPACE" 2>/dev/null | grep -q "App started successfully"; then
    echo "❌ Pod did not start successfully"
    echo "💡 Check logs: kubectl logs $POD_NAME -n $NAMESPACE"
    exit 1
fi
echo "✅ App started successfully with config from ConfigMap"

echo ""
echo "🎉 SUCCESS! ConfigMap has all required keys and pod is running!"
