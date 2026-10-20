#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
check "api-service is still in backend-ns" exists backend-ns svc/api-service
check "frontend-app calls api-service in backend-ns" field_match crossnamespace pod/frontend-app "{.spec.containers[0].command}" "api-service\.backend-ns"
check 2 "frontend-app gets an answer from the API" kubectl exec -n crossnamespace frontend-app -- wget -q -T 3 -O /dev/null http://api-service.backend-ns.svc.cluster.local
finish
