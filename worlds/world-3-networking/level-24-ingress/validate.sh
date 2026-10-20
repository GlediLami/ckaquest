#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
R="{.spec.rules[0]"
check "rule is for host myapp.local" field_eq ingress ing/web-ingress "$R.host}" myapp.local
check 2 "path is /" field_eq ingress ing/web-ingress "$R.http.paths[0].path}" /
check "pathType is Prefix" field_eq ingress ing/web-ingress "$R.http.paths[0].pathType}" Prefix
check "backend is web-service:80" out_eq "web-service 80" kubectl get ing web-ingress -n ingress -o jsonpath="$R.http.paths[0].backend.service.name} $R.http.paths[0].backend.service.port.number}"
finish
