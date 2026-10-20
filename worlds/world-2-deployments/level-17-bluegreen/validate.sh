#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
only_green() {
  local ips green
  ips="$(kubectl get endpointslices -n ckaquest -l kubernetes.io/service-name=app-service -o jsonpath="{.items[*].endpoints[*].addresses[*]}" | tr " " "\n" | sort)"
  green="$(kubectl get pods -n ckaquest -l app=myapp,version=green -o jsonpath="{.items[*].status.podIP}" | tr " " "\n" | sort)"
  [ -n "$ips" ] && [ "$ips" = "$green" ]
}
check "app-service selects version=green" field_eq ckaquest svc/app-service "{.spec.selector.version}" green
check 2 "app-service endpoints are exactly the green pods" only_green
check "app-green is ready" deploy_ready ckaquest app-green
finish
