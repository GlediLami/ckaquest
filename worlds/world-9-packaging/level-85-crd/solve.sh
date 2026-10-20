#!/usr/bin/env bash
source "$CQ_ROOT/lib/common.sh"
kubectl apply -f "$CQ_WORK/85/backup-crd.yaml"
kubectl wait --for=condition=Established crd/backups.ops.example.com --timeout=30s
cat <<'EOF' | kubectl apply -f -
apiVersion: ops.example.com/v1
kind: Backup
metadata:
  name: nightly
  namespace: crd-lab
spec:
  schedule: "0 2 * * *"
  target: postgres
  retain: 7
EOF
echo bk > "$CQ_WORK/85/shortname.txt"
