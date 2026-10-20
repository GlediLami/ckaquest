#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
check "nginx-broken uses an nginx image" field_match ckaquest pod/nginx-broken "{.spec.containers[0].image}" "^nginx(:|$)"
check 2 "nginx-broken is Running and Ready" pod_ready ckaquest nginx-broken
check "the container has not crashed since it started" field_eq ckaquest pod/nginx-broken "{.status.containerStatuses[0].restartCount}" 0
finish
