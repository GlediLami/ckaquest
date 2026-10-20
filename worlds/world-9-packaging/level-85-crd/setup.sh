#!/usr/bin/env bash
set -uo pipefail
source "$CQ_ROOT/lib/common.sh"
W="$(cq_work_dir 85)"
cat > "$W/backup-crd.yaml" <<'EOF'
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: backups.ops.example.com
spec:
  group: ops.example.com
  scope: Namespaced
  names:
    plural: backups
    singular: backup
    kind: Backup
    shortNames: [bk]
  versions:
  - name: v1
    served: true
    storage: true
    schema:
      openAPIV3Schema:
        type: object
        properties:
          spec:
            type: object
            required: [schedule, target]
            properties:
              schedule: {type: string}
              target: {type: string}
              retain: {type: integer, minimum: 1}
EOF
mv -f "$W/shortname.txt" "$W/shortname.txt.old" 2>/dev/null || true
kubectl delete crd backups.ops.example.com --ignore-not-found --timeout=60s >/dev/null
