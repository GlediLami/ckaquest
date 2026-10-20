#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
check 2 "app-config has database_host" field_eq ckaquest cm/app-config "{.data.database_host}" postgres.ckaquest.svc.cluster.local
check 2 "web-app is Ready" pod_ready ckaquest web-app
finish
