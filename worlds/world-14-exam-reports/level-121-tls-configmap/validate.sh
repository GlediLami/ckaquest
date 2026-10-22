#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
tls12() { in_cluster_out tls-lab curlimages/curl:8.11.1 curl -sk -m 5 --tlsv1.2 --tls-max 1.2 https://web.tls-lab/ | grep -q "tls ok"; }
tls13() { in_cluster_out tls-lab curlimages/curl:8.11.1 curl -sk -m 5 --tlsv1.3 https://web.tls-lab/ | grep -q "tls ok"; }
check "the ConfigMap allows TLSv1.2 and TLSv1.3" out_match "ssl_protocols +(TLSv1\.2 +TLSv1\.3|TLSv1\.3 +TLSv1\.2) *;" kubectl get cm nginx-tls -n tls-lab -o jsonpath='{.data.default\.conf}'
check 3 "a TLS 1.2 client gets 'tls ok'" tls12
check "a TLS 1.3 client still works" tls13
check 2 "ConfigMap nginx-tls is immutable" field_eq tls-lab cm/nginx-tls '{.immutable}' true
finish
