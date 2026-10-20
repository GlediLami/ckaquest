#!/usr/bin/env bash
source "$CQ_ROOT/lib/common.sh"
kubectl create clusterrole node-reader --verb=get,list,watch --resource=nodes
kubectl create clusterrolebinding node-inspector-binding --clusterrole=node-reader --serviceaccount=monitoring:node-inspector
