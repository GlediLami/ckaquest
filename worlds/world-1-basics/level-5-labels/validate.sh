#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
endpoint_is_backend() { [ -n "$(jp labels pod/backend-app "{.status.podIP}")" ] && kubectl get endpointslices -n labels -l kubernetes.io/service-name=backend-service -o jsonpath="{.items[*].endpoints[*].addresses[*]}" | grep -qw "$(jp labels pod/backend-app "{.status.podIP}")"; }
check "backend-app is Ready" pod_ready labels backend-app
check 2 "backend-service has backend-app as its endpoint" endpoint_is_backend
finish
