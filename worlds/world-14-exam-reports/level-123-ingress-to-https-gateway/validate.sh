#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
gwip() { kubectl get svc -n shop-migrate -l gateway.networking.k8s.io/gateway-name=shop-gw -o jsonpath='{.items[0].spec.clusterIP}'; }
get() { in_cluster_out shop-migrate curlimages/curl:8.11.1 curl -sk -m 5 --resolve "shop.example.com:443:$(gwip)" "https://shop.example.com$1"; }
listener() { kubectl get gateway shop-gw -n shop-migrate -o jsonpath='{range .spec.listeners[?(@.name=="https")]}{.protocol} {.port} {.hostname} {.tls.mode} {.tls.certificateRefs[0].name}{end}'; }
check "Gateway shop-gw uses class nginx" field_eq shop-migrate gateway/shop-gw '{.spec.gatewayClassName}' nginx
check 2 "listener https: HTTPS 443 shop.example.com Terminate shop-tls" out_eq "HTTPS 443 shop.example.com Terminate shop-tls" listener
check "HTTPRoute shop-route is attached to shop-gw" field_eq shop-migrate httproute/shop-route '{.spec.parentRefs[0].name}' shop-gw
check 2 "https://shop.example.com/api answers 'shop api'" out_match "shop api" get /api
check 2 "https://shop.example.com/ answers 'shop web'" out_match "shop web" get /
check "Ingress shop is deleted" not_exists shop-migrate ingress/shop
finish
