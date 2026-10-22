#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
ctrl() { kubectl get svc ingress-nginx-controller -n ingress-nginx -o jsonpath='{.spec.clusterIP}'; }
https_ok() { in_cluster_out tls-ingress curlimages/curl:8.11.1 curl -sk -m 5 --resolve "secure.example.com:443:$(ctrl)" https://secure.example.com/ | grep -q "secure app"; }
check "Secret app-tls is type kubernetes.io/tls" field_eq tls-ingress secret/app-tls '{.type}' kubernetes.io/tls
check "Ingress uses class nginx" field_eq tls-ingress ing/app-ingress '{.spec.ingressClassName}' nginx
check 2 "TLS for secure.example.com with app-tls" out_eq "secure.example.com app-tls" kubectl get ing app-ingress -n tls-ingress -o jsonpath='{.spec.tls[0].hosts[0]} {.spec.tls[0].secretName}'
check 3 "https://secure.example.com answers 'secure app'" https_ok
finish
