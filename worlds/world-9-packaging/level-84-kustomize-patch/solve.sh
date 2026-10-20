#!/usr/bin/env bash
source "$CQ_ROOT/lib/common.sh"
O="$CQ_WORK/84/overlays/prod"
mkdir -p "$O"
cat > "$O/limits.yaml" <<'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
spec:
  template:
    spec:
      containers:
      - name: web
        resources:
          limits:
            memory: 128Mi
            cpu: 200m
        envFrom:
        - configMapRef:
            name: web-config
EOF
cat > "$O/kustomization.yaml" <<'EOF'
resources:
- ../../base
namespace: kustomize-patch
patches:
- path: limits.yaml
configMapGenerator:
- name: web-config
  literals:
  - MODE=production
EOF
kubectl apply -k "$O"
kubectl rollout status deploy/web -n kustomize-patch --timeout=120s
