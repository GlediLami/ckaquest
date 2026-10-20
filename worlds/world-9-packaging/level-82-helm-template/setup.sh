#!/usr/bin/env bash
set -uo pipefail
source "$CQ_ROOT/lib/common.sh"
"$CQ_ROOT/bin/cq-helm-repo" ensure >/dev/null
for r in $(helm list -n helm-render -aq 2>/dev/null); do helm uninstall "$r" -n helm-render >/dev/null 2>&1; done
W="$(cq_work_dir 82)"; mv -f "$W/preview.yaml" "$W/preview.yaml.old" 2>/dev/null || true
