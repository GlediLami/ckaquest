#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
SA=system:serviceaccount:backup-system:backup-operator
works() { ! kubectl logs deploy/backup-operator -n backup-system --tail=1 2>/dev/null | grep -qi forbidden; }
check 2 "operator can list backups in all namespaces" can_i "$SA" list backups.ops.example.com
check "operator can watch backups" can_i "$SA" watch backups.ops.example.com
status_ok() { [ "$(kubectl auth can-i patch backups.ops.example.com --subresource=status --as="$SA" -A 2>/dev/null)" = yes ]; }
check "operator can patch backups/status" status_ok
check "operator cannot delete backups" cannot_i "$SA" delete backups.ops.example.com
check "operator cannot list pods" cannot_i "$SA" list pods
check 2 "operator log shows no Forbidden" works
finish
