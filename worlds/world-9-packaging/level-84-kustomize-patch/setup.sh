#!/usr/bin/env bash
set -uo pipefail
source "$CQ_ROOT/lib/common.sh"
W="$(cq_work_dir 84)"
mkdir -p "$W/base"
cat > "$W/base/deployment.yaml" <<'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
spec:
  replicas: 1
  selector:
    matchLabels: {app: web}
  template:
    metadata:
      labels: {app: web}
    spec:
      containers:
      - name: web
        image: nginx:1.27-alpine
        ports:
        - containerPort: 80
EOF
cat > "$W/base/service.yaml" <<'EOF'
apiVersion: v1
kind: Service
metadata:
  name: web
spec:
  selector: {app: web}
  ports:
  - port: 80
EOF
cat > "$W/base/kustomization.yaml" <<'EOF'
resources:
- deployment.yaml
- service.yaml
EOF
mv -f "$W/overlays" "$W/overlays.old.$(date +%s)" 2>/dev/null || true
