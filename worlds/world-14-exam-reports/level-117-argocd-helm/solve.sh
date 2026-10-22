#!/usr/bin/env bash
source "$CQ_ROOT/lib/common.sh"
source "$CQ_ROOT/cluster/versions.env"
helm repo add argo http://127.0.0.1:8879 >/dev/null
helm repo update argo >/dev/null
helm template argocd argo/argo-cd --version "$ARGOCD_CHART_VERSION" -n argocd --set crds.install=false > "$CQ_WORK/117/argocd.yaml"
helm install argocd argo/argo-cd --version "$ARGOCD_CHART_VERSION" -n argocd --set crds.install=false >/dev/null
