#!/usr/bin/env bash
source "$CQ_ROOT/lib/common.sh"
helm rollback blog 2 -n helm-blog --wait
