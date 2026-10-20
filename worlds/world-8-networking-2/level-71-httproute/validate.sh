#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
curl_host() { in_cluster_out "$1" curlimages/curl:8.11.1 curl -s -m 5 -H "Host: $2" "http://$(gw_addr "$3")$4"; }
route_ok() { [ "$(kubectl get httproute "$2" -n "$1" -o jsonpath='{.status.parents[0].conditions[?(@.type=="Accepted")].status} {.status.parents[0].conditions[?(@.type=="ResolvedRefs")].status}')" = "True True" ]; }
check "HTTPRoute shop-route attaches to web-gw" field_eq shop httproute/shop-route '{.spec.parentRefs[0].name}' web-gw
check "it matches host shop.example.com" field_eq shop httproute/shop-route '{.spec.hostnames[0]}' shop.example.com
check "route is Accepted and its backend resolves" route_ok shop shop-route
check 3 "shop.example.com through the Gateway answers 'shop frontend'" out_match "shop frontend" curl_host shop shop.example.com web-gw /
finish
