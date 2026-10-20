#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
endpoint_has() { local ip; ip="$(jp ckaquest "pod/$2" "{.status.podIP}")"; [ -n "$ip" ] && kubectl get endpointslices -n ckaquest -l kubernetes.io/service-name="$1" -o jsonpath="{.items[*].endpoints[*].addresses[*]}" | grep -qw "$ip"; }
check "backend-pod labels are unchanged (app=backend)" field_eq ckaquest pod/backend-pod "{.metadata.labels.app}" backend
check 2 "backend-service has backend-pod as endpoint" endpoint_has backend-service backend-pod
check "test-client gets an answer from backend-service" kubectl exec -n ckaquest test-client -- curl -s -o /dev/null -m 5 http://backend-service
finish
