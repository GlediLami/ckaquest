#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
curl_host() { in_cluster_out "$1" curlimages/curl:8.11.1 curl -s -m 5 -H "Host: $2" "http://$(gw_addr "$3")$4"; }
route_ok() { [ "$(kubectl get httproute "$2" -n "$1" -o jsonpath='{.status.parents[0].conditions[?(@.type=="Accepted")].status} {.status.parents[0].conditions[?(@.type=="ResolvedRefs")].status}')" = "True True" ]; }
weights() { kubectl get httproute api-route -n api-split -o jsonpath='{range .spec.rules[0].backendRefs[*]}{.name}={.weight} {end}'; }
both_seen() {
  local out; out="$(in_cluster_out api-split curlimages/curl:8.11.1 sh -c 'for i in $(seq 40); do curl -s -m 3 -H "Host: api.example.com" http://'"$(gw_addr web-gw)"'/; done')"
  grep -q "api v1" <<<"$out" && grep -q "api v2" <<<"$out"
}
check 2 "weights are api-v1=80 and api-v2=20" out_match "api-v1=80 api-v2=20|api-v2=20 api-v1=80" weights
check "api-route is Accepted and resolves" route_ok api-split api-route
check 2 "40 requests reach both versions" both_seen
finish
