#!/usr/bin/env bash
set -uo pipefail
source "$CQ_ROOT/lib/common.sh"
W="$(cq_work_dir 130)"
cat > "$W/policy-1.yaml" <<'EOF'
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-any-namespace
  namespace: np-pick
spec:
  podSelector:
    matchLabels:
      app: backend
  policyTypes: ["Ingress"]
  ingress:
  - from:
    - namespaceSelector: {}
    ports:
    - protocol: TCP
      port: 8080
EOF
cat > "$W/policy-2.yaml" <<'EOF'
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-frontend-all-ports
  namespace: np-pick
spec:
  podSelector:
    matchLabels:
      app: backend
  policyTypes: ["Ingress"]
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: frontend
EOF
cat > "$W/policy-3.yaml" <<'EOF'
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-frontend-8080
  namespace: np-pick
spec:
  podSelector:
    matchLabels:
      app: backend
  policyTypes: ["Ingress"]
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: frontend
    ports:
    - protocol: TCP
      port: 8080
EOF
cat > "$W/policy-4.yaml" <<'EOF'
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-everyone
  namespace: np-pick
spec:
  podSelector:
    matchLabels:
      app: backend
  policyTypes: ["Ingress"]
  ingress:
  - {}
EOF
cat > "$W/policy-5.yaml" <<'EOF'
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-front-8080
  namespace: np-pick
spec:
  podSelector:
    matchLabels:
      app: backend
  policyTypes: ["Ingress"]
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: front
    ports:
    - protocol: TCP
      port: 8080
EOF
cat <<'EOF' | kubectl apply -f - >/dev/null
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all
  namespace: np-pick
spec:
  podSelector: {}
  policyTypes: ["Ingress"]
EOF
kubectl run backend -n np-pick --image=hashicorp/http-echo:1.0 --labels=app=backend --port=8080 -- -text=backend -listen=:8080 >/dev/null
kubectl expose pod backend -n np-pick --port=8080 >/dev/null
kubectl run frontend -n np-pick --image=busybox:1.36 --labels=app=frontend -- sleep 3600 >/dev/null
kubectl run other -n np-pick --image=busybox:1.36 --labels=app=other -- sleep 3600 >/dev/null
kubectl wait --for=condition=Ready pod --all -n np-pick --timeout=120s >/dev/null 2>&1 || true
