#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
rel() { helm status "$1" -n "$2" >/dev/null 2>&1; }
norel() { ! rel "$@"; }
check 2 "old-api (webapp-1.0.0) is gone" norel old-api helm-team-a
check 2 "old-web (webapp-1.0.0) is gone" norel old-web helm-team-b
check "new-api is still installed" rel new-api helm-team-a
check "portal is still installed" rel portal helm-audit
finish
