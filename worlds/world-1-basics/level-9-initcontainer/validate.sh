#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
check "Service backend-service exists in initcontainer" exists initcontainer svc/backend-service
check "the init container finished" field_eq initcontainer pod/web-with-init "{.status.initContainerStatuses[0].state.terminated.reason}" Completed
check 2 "web-with-init is Ready" pod_ready initcontainer web-with-init
finish
