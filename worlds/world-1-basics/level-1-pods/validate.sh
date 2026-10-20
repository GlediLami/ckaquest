#!/bin/bash

echo "🔍 Checking pod status..."

# Check if pod exists
if ! kubectl get pod nginx-broken -n ckaquest &>/dev/null; then
  echo "❌ Pod 'nginx-broken' not found in namespace ckaquest"
  exit 1
fi

# Get pod status
STATUS=$(kubectl get pod nginx-broken -n ckaquest -o jsonpath='{.status.phase}' 2>/dev/null)
READY=$(kubectl get pod nginx-broken -n ckaquest -o jsonpath='{.status.containerStatuses[0].ready}' 2>/dev/null)

echo "   Phase: $STATUS"
echo "   Ready: $READY"

# Check if pod is running AND ready
if [[ "$STATUS" == "Running" ]] && [[ "$READY" == "true" ]]; then
  # Verify the command is correct (not the broken "nginxzz")
  COMMAND=$(kubectl get pod nginx-broken -n ckaquest -o jsonpath='{.spec.containers[0].command[0]}' 2>/dev/null)
  
  if [[ "$COMMAND" == "nginxzz" ]]; then
    echo "❌ Pod still has broken command 'nginxzz'"
    echo "💡 Hint: Delete the pod and apply the fixed solution.yaml"
    exit 1
  fi
  
  echo "✅ Level complete! Pod is running correctly"
  exit 0
else
  echo "❌ Pod is not running properly"
  echo "💡 Current status: $STATUS"
  echo "💡 Hint: Check 'kubectl describe pod nginx-broken -n ckaquest' for errors"
  exit 1
fi
