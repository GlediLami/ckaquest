#!/bin/bash
set -e

WORLD_DIR="worlds/world-1-basics"

for LEVEL in "$WORLD_DIR"/*; do
  echo "=================================="
  echo "▶ Starting $(basename $LEVEL)"
  echo "=================================="

  kubectl delete namespace k8squest --ignore-not-found
  kubectl create namespace k8squest

  kubectl apply -n k8squest -f "$LEVEL/broken.yaml"

  echo "❌ Mission deployed. Fix the issue."
  echo "Press ENTER when ready to validate"
  read

  sh "$LEVEL/validate.sh"

done

echo "🎉 World 1 completed!"
