#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
from() { kubectl exec "$1" -n np-pick -- wget -qO- -T 3 http://backend:8080 2>/dev/null | grep -q backend; }
policies() { kubectl get netpol -n np-pick -o jsonpath='{range .items[*]}{.metadata.name}{"\n"}{end}' | sort | paste -sd' '; }
check 3 "only deny-all and allow-frontend-8080 are applied" out_eq "allow-frontend-8080 deny-all" policies
check "frontend reaches backend on 8080" from frontend
check "other is still blocked" bash -c "! kubectl exec other -n np-pick -- wget -qO- -T 3 http://backend:8080 >/dev/null 2>&1" 
finish
