#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
C='{.spec.template.spec.containers[0]'
check "deploy.yaml exists and is a Deployment shop" file_contains "$CQ_WORK/107/deploy.yaml" "name: shop"
check "MODE=prod" field_eq drill-107 deploy/shop "$C.env[?(@.name==\"MODE\")].value}" prod
check "requests 50m / 32Mi" out_eq "50m 32Mi" kubectl get deploy shop -n drill-107 -o jsonpath="$C.resources.requests.cpu} $C.resources.requests.memory}"
check "readiness probe GET / on 80" out_eq "/ 80" kubectl get deploy shop -n drill-107 -o jsonpath="$C.readinessProbe.httpGet.path} $C.readinessProbe.httpGet.port}"
check 2 "shop has 2/2 ready replicas" deploy_ready drill-107 shop 2
finish
