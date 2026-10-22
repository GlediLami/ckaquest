#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
F="$CQ_WORK/117/argocd.yaml"
values() { helm get values argocd -n argocd -o json 2>/dev/null; }
check "repo argo is added" out_match "^argo[[:space:]]" helm repo list
check "argocd.yaml exists" file_exists "$F"
check "it renders argocd-server in namespace argocd" bash -c "grep -q 'name: argocd-server' '$F' && grep -q 'namespace: argocd' '$F'"
check 2 "it has no CustomResourceDefinition" bash -c "! grep -q 'kind: CustomResourceDefinition' '$F'"
check 2 "release argocd is deployed with chart argo-cd-10.10.3" out_match "argo-cd-10.10.3.*deployed|deployed.*argo-cd-10.10.3" bash -c "helm list -n argocd | grep '^argocd'"
check "the release has crds.install=false" out_match '"install":false' values
check "Deployment argocd-server exists" exists argocd deploy/argocd-server
finish
