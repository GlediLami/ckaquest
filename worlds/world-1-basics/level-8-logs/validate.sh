#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
stable() { local a b; a="$(jp logs pod/database-app "{.status.containerStatuses[0].restartCount}")"; sleep 5; b="$(jp logs pod/database-app "{.status.containerStatuses[0].restartCount}")"; [ "$a" = "$b" ]; }
check 2 "database-app is Ready" pod_ready logs database-app
check "the database accepts connections" kubectl exec -n logs database-app -- pg_isready -q
check "no restarts in the last 5 seconds" stable
finish
