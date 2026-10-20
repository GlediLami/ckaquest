#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
check "client-app runs in ckaquest" pod_ready ckaquest client-app
check "backend-service exists in ckaquest" exists ckaquest svc/backend-service
check "no client-app left in default" not_exists default pod/client-app
check "no backend-service left in default" not_exists default svc/backend-service
finish
