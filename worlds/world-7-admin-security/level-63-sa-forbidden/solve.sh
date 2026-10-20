#!/usr/bin/env bash
source "$CQ_ROOT/lib/common.sh"
kubectl create role cm-reader -n reports --verb=get,list --resource=configmaps
kubectl create rolebinding cm-reader-binding -n reports --role=cm-reader --serviceaccount=reports:report-sa
sleep 12
