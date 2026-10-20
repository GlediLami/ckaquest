#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
probe() { [ "$(jp ckaquest "pod/$1" "{.spec.containers[0].readinessProbe.httpGet.path} {.spec.containers[0].readinessProbe.httpGet.port}")" = "/ 8080" ]; }
check "web-app-1 has a readiness probe GET / on 8080" probe web-app-1
check "web-app-2 has a readiness probe GET / on 8080" probe web-app-2
check "web-app-1 is Ready" pod_ready ckaquest web-app-1
check "web-app-2 is Ready" pod_ready ckaquest web-app-2
finish
