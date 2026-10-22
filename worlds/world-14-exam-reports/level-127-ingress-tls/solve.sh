#!/usr/bin/env bash
source "$CQ_ROOT/lib/common.sh"
kubectl create secret tls app-tls -n tls-ingress --cert="$CQ_WORK/127/tls.crt" --key="$CQ_WORK/127/tls.key"
kubectl create ingress app-ingress -n tls-ingress --class=nginx --rule="secure.example.com/*=app:80,tls=app-tls"
ok() { kubectl run "cq-wait-$RANDOM" -n tls-ingress --image=curlimages/curl:8.11.1 --restart=Never --rm -i --quiet --command -- curl -sk -m 5 --resolve "secure.example.com:443:$(kubectl get svc ingress-nginx-controller -n ingress-nginx -o jsonpath='{.spec.clusterIP}')" https://secure.example.com/ | grep -q "secure app"; }
cq_wait 240 ok
