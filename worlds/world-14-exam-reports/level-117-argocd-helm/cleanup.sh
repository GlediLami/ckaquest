#!/usr/bin/env bash
source "$CQ_ROOT/lib/common.sh"
helm uninstall argocd -n argocd >/dev/null 2>&1
kubectl delete crd applications.argoproj.io applicationsets.argoproj.io appprojects.argoproj.io --ignore-not-found --wait=false >/dev/null 2>&1
helm repo remove argo >/dev/null 2>&1
true
