#!/usr/bin/env bash
set -uo pipefail
source "$CQ_ROOT/lib/common.sh"
W="$(cq_work_dir 103)"; for f in "$W"/*; do [ -e "$f" ] && mv -f "$f" "$f.old"; done; true
