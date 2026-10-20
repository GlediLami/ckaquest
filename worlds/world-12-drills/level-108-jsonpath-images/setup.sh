#!/usr/bin/env bash
set -uo pipefail
source "$CQ_ROOT/lib/common.sh"
W="$(cq_work_dir 108)"; for f in "$W"/*; do [ -e "$f" ] && mv -f "$f" "$f.old"; done; true
mk() {
cat <<EOF | kubectl apply -f - >/dev/null
apiVersion: v1
kind: Pod
metadata:
  name: $1
  namespace: drill-108
  labels: {app: $2}
spec:
  containers:
  - {name: main, image: nginx:1.27-alpine}
  - {name: sidecar, image: $3, command: [sleep, "3600"]}
EOF
}
mk shop-1 shop busybox:1.36
mk shop-2 shop busybox:1.37
mk blog-1 blog busybox:1.36
