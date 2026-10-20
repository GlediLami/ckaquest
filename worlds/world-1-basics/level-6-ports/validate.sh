#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
check "web-server is Ready" pod_ready ckaquest web-server
check "web-service targets a port nginx listens on" out_match "^(80|http)$" kubectl get svc web-service -n ckaquest -o jsonpath="{.spec.ports[0].targetPort}"
check 2 "a request to web-service:80 gets an answer" in_cluster_ok ckaquest busybox:1.36 wget -q -T 5 -O /dev/null http://web-service
finish
