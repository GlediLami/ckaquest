#!/usr/bin/env bash
source "$CQ_ROOT/lib/common.sh"
kubectl apply -f "$CQ_WORK/130/policy-3.yaml"
sleep 5
