#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
https_ok() { in_cluster_out secure-shop curlimages/curl:8.11.1 curl -sk -m 5 --resolve "secure.example.com:443:$(kubectl get svc -n secure-shop -l gateway.networking.k8s.io/gateway-name=web-gw -o jsonpath='{.items[0].spec.clusterIP}')" https://secure.example.com/ | grep -q "secure shop"; }
listener() { kubectl get gateway web-gw -n secure-shop -o jsonpath='{range .spec.listeners[?(@.name=="https")]}{.protocol} {.port} {.hostname} {.tls.mode} {.tls.certificateRefs[0].name}{end}'; }
check "Secret secure-tls is type kubernetes.io/tls" field_eq secure-shop secret/secure-tls '{.type}' kubernetes.io/tls
check 2 "listener https: HTTPS 443 secure.example.com Terminate secure-tls" out_eq "HTTPS 443 secure.example.com Terminate secure-tls" listener
check "HTTP listener is still there" field_eq secure-shop gateway/web-gw '{.spec.listeners[?(@.name=="http")].port}' 80
check 3 "https://secure.example.com answers 'secure shop'" https_ok
finish
