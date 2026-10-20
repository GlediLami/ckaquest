#!/usr/bin/env bash
source "$CQ_ROOT/lib/common.sh"
"$CQ_ROOT/bin/cq-cluster" lab-down >/dev/null 2>&1
true
