#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
check "pod web with tier=web" field_eq drill-106 pod/web '{.metadata.labels.tier}' web
check "deployment api has 3 ready replicas" deploy_ready drill-106 api 3
check "service api selects the api pods" field_eq drill-106 svc/api '{.spec.selector.app}' api
check "configmap cfg mode=fast" field_eq drill-106 cm/cfg '{.data.mode}' fast
check "secret token t=abc123" out_eq abc123 sh -c "kubectl get secret token -n drill-106 -o jsonpath='{.data.t}' | base64 -d"
check "serviceaccount bot exists" exists drill-106 sa/bot
check 2 "bot can list pods, not delete them" sh -c "[ \"\$(kubectl auth can-i list pods -n drill-106 --as=system:serviceaccount:drill-106:bot)\" = yes ] && [ \"\$(kubectl auth can-i delete pods -n drill-106 --as=system:serviceaccount:drill-106:bot)\" = no ]"
finish
