#!/usr/bin/env bash
source "$CQ_ROOT/lib/common.sh"
N="-n drill-106"
kubectl run web $N --image=nginx:1.27-alpine -l tier=web
kubectl create deployment api $N --image=nginx:1.27-alpine --replicas=3
kubectl expose deployment api $N --port=80
kubectl create configmap cfg $N --from-literal=mode=fast
kubectl create secret generic token $N --from-literal=t=abc123
kubectl create serviceaccount bot $N
kubectl create role pod-reader $N --verb=get,list --resource=pods
kubectl create rolebinding bot-pod-reader $N --role=pod-reader --serviceaccount=drill-106:bot
kubectl rollout status deploy/api $N --timeout=90s
