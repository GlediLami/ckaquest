#!/usr/bin/env bash
source "$CQ_ROOT/lib/common.sh"
cat <<'EOF' | kubectl apply -f -
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: mariadb
  namespace: mariadb
spec:
  accessModes: ["ReadWriteOnce"]
  storageClassName: mariadb-storage
  volumeName: mariadb-pv
  resources:
    requests:
      storage: 250Mi
EOF
sed 's/claimName: ""/claimName: mariadb/' "$CQ_WORK/119/mariadb-deploy.yaml" | kubectl apply -f -
kubectl rollout status deploy/mariadb -n mariadb --timeout=120s
