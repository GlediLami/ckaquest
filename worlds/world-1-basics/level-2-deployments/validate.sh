#!/bin/bash
READY=$(kubectl get deploy web -n k8squest -o jsonpath='{.status.readyReplicas}' 2>/dev/null || echo 0)

if [[ "$READY" -ge 1 ]]; then
  echo "✅ Deployment fixed!"
else
  echo "❌ No ready replicas"
  exit 1
fi
