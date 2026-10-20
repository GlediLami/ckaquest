#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
check 2 "sessionAffinity is ClientIP" field_eq sessionaffinity svc/session-service "{.spec.sessionAffinity}" ClientIP
check "session-service still has 3 endpoints" out_eq 3 sh -c "kubectl get endpointslices -n sessionaffinity -l kubernetes.io/service-name=session-service -o jsonpath=\"{.items[*].endpoints[*].addresses[*]}\" | wc -w"
finish
