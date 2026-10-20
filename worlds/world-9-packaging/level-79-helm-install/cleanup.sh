#!/usr/bin/env bash
source "$CQ_ROOT/lib/common.sh"
for r in $(helm list -n helm-shop -aq 2>/dev/null); do helm uninstall "$r" -n helm-shop >/dev/null 2>&1; done
true
