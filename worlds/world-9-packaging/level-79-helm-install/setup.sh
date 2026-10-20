#!/usr/bin/env bash
set -uo pipefail
source "$CQ_ROOT/lib/common.sh"
"$CQ_ROOT/bin/cq-helm-repo" ensure >/dev/null
for r in $(helm list -n helm-shop -aq 2>/dev/null); do helm uninstall "$r" -n helm-shop >/dev/null 2>&1; done
helm repo remove cq >/dev/null 2>&1 || true
