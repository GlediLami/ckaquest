#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
endpoint_is_backend() { [ -n "$(jp ckaquest pod/backend-app "{.status.podIP}")" ] && kubectl get endpointslices -n ckaquest -l kubernetes.io/service-name=backend-service -o jsonpath="{.items[*].endpoints[*].addresses[*]}" | grep -qw "$(jp ckaquest pod/backend-app "{.status.podIP}")"; }
check "backend-app is Ready" pod_ready ckaquest backend-app
check 2 "backend-service has backend-app as its endpoint" endpoint_is_backend
finish
