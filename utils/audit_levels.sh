#!/bin/bash

# Audit all 50 levels for validation and namespace issues

echo "🔍 Auditing all 50 K8sQuest levels..."
echo "======================================"
echo ""

TOTAL=0
MISSING_NAMESPACE=0
WEAK_VALIDATION=0

for level_dir in worlds/*/level-*; do
  TOTAL=$((TOTAL + 1))
  level_name=$(basename "$level_dir")
  world=$(basename $(dirname "$level_dir"))
  
  # Check for broken.yaml
  if [[ -f "$level_dir/broken.yaml" ]]; then
    # Check if namespace is missing
    if ! grep -q "namespace: k8squest" "$level_dir/broken.yaml"; then
      echo "⚠️  $world/$level_name: broken.yaml missing namespace"
      MISSING_NAMESPACE=$((MISSING_NAMESPACE + 1))
    fi
  fi
  
  # Check validation script
  if [[ -f "$level_dir/validate.sh" ]]; then
    # Check if it has basic status checks
    if ! grep -q "ready\|Ready\|READY" "$level_dir/validate.sh" 2>/dev/null; then
      # Some resources may not have ready status (ConfigMaps, Secrets, etc)
      # Flag for manual review
      resource_type=$(grep -o "kind: \w*" "$level_dir/broken.yaml" 2>/dev/null | head -1 | cut -d' ' -f2)
      if [[ "$resource_type" =~ ^(Pod|Deployment|StatefulSet|DaemonSet|Job)$ ]]; then
        echo "⚠️  $world/$level_name: validate.sh may lack readiness check"
        WEAK_VALIDATION=$((WEAK_VALIDATION + 1))
      fi
    fi
  fi
done

echo ""
echo "======================================"
echo "📊 Audit Summary:"
echo "  Total levels: $TOTAL"
echo "  Missing namespace: $MISSING_NAMESPACE"
echo "  Potential weak validation: $WEAK_VALIDATION"
echo "======================================"
