#!/usr/bin/env bash
# The broken state lives in "default". Remove only the two objects this level creates there.
kubectl delete pod client-app -n default --ignore-not-found --wait=false >/dev/null 2>&1
kubectl delete svc backend-service -n default --ignore-not-found >/dev/null 2>&1
true
