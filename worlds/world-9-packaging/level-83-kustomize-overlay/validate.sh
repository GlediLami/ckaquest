#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
check "base is unchanged (replicas 1)" file_contains "$CQ_WORK/83/base/deployment.yaml" "replicas: 1"
check "overlay kustomization exists" file_exists "$CQ_WORK/83/overlays/prod/kustomization.yaml"
check 2 "Deployment prod-web runs 3 ready replicas" deploy_ready kustomize-prod prod-web 3
check 2 "prod-web uses nginx:1.28-alpine" field_eq kustomize-prod deploy/prod-web '{.spec.template.spec.containers[0].image}' nginx:1.28-alpine
check "Service prod-web exists" exists kustomize-prod svc/prod-web
finish
