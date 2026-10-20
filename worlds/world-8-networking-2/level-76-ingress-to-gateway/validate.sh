#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
curl_host() { in_cluster_out "$1" curlimages/curl:8.11.1 curl -s -m 5 -H "Host: $2" "http://$(gw_addr "$3")$4"; }
route_ok() { [ "$(kubectl get httproute "$2" -n "$1" -o jsonpath='{.status.parents[0].conditions[?(@.type=="Accepted")].status} {.status.parents[0].conditions[?(@.type=="ResolvedRefs")].status}')" = "True True" ]; }
check "Ingress legacy is gone" not_exists migrate-lab ing/legacy
check "app-route is Accepted and resolves" route_ok migrate-lab app-route
check 2 "/api/users goes to api" out_match "api backend" curl_host migrate-lab app.example.com web-gw /api/users
check 2 "/ goes to web" out_match "web frontend" curl_host migrate-lab app.example.com web-gw /
finish
