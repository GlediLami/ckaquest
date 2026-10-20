#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
check 2 "frontend reaches backend-service:8080" kubectl exec -n networkpolicy frontend -- wget -q -T 3 -O /dev/null http://backend-service:8080
check 2 "another pod is still blocked" in_cluster_fails networkpolicy busybox:1.36 wget -q -T 3 -O /dev/null http://backend-service:8080
check "backend-network-policy still exists" exists networkpolicy netpol/backend-network-policy
finish
