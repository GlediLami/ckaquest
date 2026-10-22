#!/usr/bin/env bash
set -uo pipefail
source "$CQ_ROOT/lib/common.sh"
W="$(cq_work_dir 129)"; [ -e "$W/token.txt" ] && mv -f "$W/token.txt" "$W/token.txt.old"; [ -e "$W/staticpodpath.txt" ] && mv -f "$W/staticpodpath.txt" "$W/staticpodpath.txt.old"; true
kubectl create secret generic api-token -n debug-lab --from-literal=token="$(openssl rand -hex 8)" >/dev/null
cat <<'EOF' | kubectl apply -f - >/dev/null
apiVersion: v1
kind: Pod
metadata:
  name: api
  namespace: debug-lab
spec:
  containers:
  - name: api
    image: hashicorp/http-echo:1.0
    args: ["-text=api", "-listen=:5678"]
    env:
    - name: API_TOKEN
      valueFrom:
        secretKeyRef:
          name: api-token
          key: token
EOF
kubectl wait --for=condition=Ready pod/api -n debug-lab --timeout=120s >/dev/null 2>&1 || true
