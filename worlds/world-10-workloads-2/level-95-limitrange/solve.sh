#!/usr/bin/env bash
source "$CQ_ROOT/lib/common.sh"
cat <<'EOF' | kubectl apply -f -
apiVersion: v1
kind: LimitRange
metadata:
  name: container-defaults
  namespace: team-ns
spec:
  limits:
  - type: Container
    defaultRequest: {cpu: 100m, memory: 64Mi}
    default: {cpu: 200m, memory: 128Mi}
    max: {cpu: 500m, memory: 256Mi}
EOF
kubectl run plain -n team-ns --image=nginx:1.27-alpine
