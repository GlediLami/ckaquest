#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
check "client-app runs in team-a" pod_ready team-a client-app
check "backend-service exists in team-a" exists team-a svc/backend-service
check "no client-app left in default" not_exists default pod/client-app
check "no backend-service left in default" not_exists default svc/backend-service
finish
