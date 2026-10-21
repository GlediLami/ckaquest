#!/usr/bin/env bash
set -uo pipefail
source "$CQ_ROOT/lib/common.sh"
W="$(cq_work_dir 116)"; [ -e "$W/answers.txt" ] && mv -f "$W/answers.txt" "$W/answers.txt.old"; true
