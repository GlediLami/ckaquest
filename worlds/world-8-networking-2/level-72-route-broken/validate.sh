#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
curl_host() { in_cluster_out "$1" curlimages/curl:8.11.1 curl -s -m 5 -H "Host: $2" "http://$(gw_addr "$3")$4"; }
route_ok() { [ "$(kubectl get httproute "$2" -n "$1" -o jsonpath='{.status.parents[0].conditions[?(@.type=="Accepted")].status} {.status.parents[0].conditions[?(@.type=="ResolvedRefs")].status}')" = "True True" ]; }
check "Gateway web-gw is unchanged" field_eq blog gateway/web-gw '{.spec.listeners[0].port}' 80
check "Service blog is unchanged" field_eq blog svc/blog '{.spec.ports[0].port}' 80
check 2 "blog-route is Accepted and resolves" route_ok blog blog-route
check 2 "blog.example.com answers 'blog home'" out_match "blog home" curl_host blog blog.example.com web-gw /
finish
