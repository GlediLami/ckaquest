#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
check "nginx-broken uses an nginx image" field_match pods-lab pod/nginx-broken "{.spec.containers[0].image}" "^nginx(:|$)"
check 2 "nginx-broken is Running and Ready" pod_ready pods-lab nginx-broken
check "the container has not crashed since it started" field_eq pods-lab pod/nginx-broken "{.status.containerStatuses[0].restartCount}" 0
finish
