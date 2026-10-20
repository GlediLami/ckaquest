#!/bin/bash

# Check if NodePort is explicitly set
NODEPORT=$(kubectl get svc web-nodeport -n k8squest -o jsonpath='{.spec.ports[0].nodePort}' 2>/dev/null)

if [[ -z "$NODEPORT" ]]; then
  echo "❌ Service not found"
  exit 1
fi

# Check if NodePort is in the valid range and explicitly set (30080)
if [[ "$NODEPORT" == "30080" ]]; then
  echo "✅ Level complete! NodePort explicitly configured"
  exit 0
else
  echo "❌ NodePort is $NODEPORT (random). Set nodePort: 30080 explicitly"
  exit 1
fi
