#!/usr/bin/env bash
source "$CQ_ROOT/lib/common.sh"
kubectl create secret tls secure-tls -n secure-shop --cert="$CQ_WORK/74/tls.crt" --key="$CQ_WORK/74/tls.key"
kubectl patch gateway web-gw -n secure-shop --type=json -p '[{"op":"add","path":"/spec/listeners/-","value":{"name":"https","protocol":"HTTPS","port":443,"hostname":"secure.example.com","tls":{"mode":"Terminate","certificateRefs":[{"kind":"Secret","name":"secure-tls"}]}}}]'
kubectl patch httproute secure-route -n secure-shop --type=json -p '[{"op":"add","path":"/spec/parentRefs/-","value":{"name":"web-gw","sectionName":"https"}}]'
sleep 10
