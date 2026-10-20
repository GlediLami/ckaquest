#!/usr/bin/env bash
set -uo pipefail
source "$CQ_ROOT/lib/common.sh"
W="$(cq_work_dir 105)"; for f in "$W"/*; do [ -e "$f" ] && mv -f "$f" "$f.old"; done; true
for s in 3Gi:a 500Mi:b 10Gi:c 1Gi:d; do
cat <<EOF | kubectl apply -f - >/dev/null
apiVersion: v1
kind: PersistentVolume
metadata:
  name: drill-pv-${s#*:}
spec:
  capacity: {storage: ${s%:*}}
  accessModes: [ReadWriteOnce]
  storageClassName: drill
  hostPath: {path: /tmp/drill-pv}
EOF
done
