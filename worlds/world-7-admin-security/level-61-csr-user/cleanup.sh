#!/usr/bin/env bash
source "$CQ_ROOT/lib/common.sh"
kubectl delete csr jane --ignore-not-found >/dev/null 2>&1
true
