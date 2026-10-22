#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
ip() { kubectl get pod legacy-backend -n legacy-host -o jsonpath='{.status.podIP}'; }
reach() { in_cluster_out ext-lab curlimages/curl:8.11.1 curl -s -m 5 http://legacy.ext-lab | grep -q "legacy backend"; }
check "Service legacy has no selector" field_eq ext-lab svc/legacy '{.spec.selector}' ""
check "Service port 80 is named http" out_eq "http 80" kubectl get svc legacy -n ext-lab -o jsonpath='{.spec.ports[0].name} {.spec.ports[0].port}'
check 2 "EndpointSlice legacy-1 belongs to Service legacy" field_eq ext-lab endpointslice/legacy-1 '{.metadata.labels.kubernetes\.io/service-name}' legacy
check "it points at the backend pod's IP, port http 5678" out_eq "IPv4 $(ip) http 5678" kubectl get endpointslice legacy-1 -n ext-lab -o jsonpath='{.addressType} {.endpoints[0].addresses[0]} {.ports[0].name} {.ports[0].port}'
check 3 "http://legacy.ext-lab answers 'legacy backend'" reach
finish
