#!/usr/bin/env bash
source "$CQ_ROOT/lib/common.sh"
mkdir -p "$CQ_WORK/83/overlays/prod"
cat > "$CQ_WORK/83/overlays/prod/kustomization.yaml" <<'EOF'
resources:
- ../../base
namespace: kustomize-prod
namePrefix: prod-
replicas:
- name: web
  count: 3
images:
- name: nginx
  newTag: 1.28-alpine
EOF
kubectl apply -k "$CQ_WORK/83/overlays/prod"
kubectl rollout status deploy/prod-web -n kustomize-prod --timeout=120s
