#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
SA=system:serviceaccount:agg-lab:monitor
check 2 "monitoring aggregates the label rbac.ckaquest.io/aggregate-to-monitoring" field_eq - clusterrole/monitoring '{.aggregationRule.clusterRoleSelectors[0].matchLabels.rbac\.ckaquest\.io/aggregate-to-monitoring}' true
check "monitoring-pods and monitoring-nodes carry the label" out_eq "monitoring-nodes monitoring-pods" bash -c "kubectl get clusterrole -l rbac.ckaquest.io/aggregate-to-monitoring=true -o name | cut -d/ -f2 | sort | paste -sd' '"
check "ClusterRoleBinding monitoring binds monitoring to agg-lab/monitor" out_eq "monitoring ServiceAccount monitor agg-lab" kubectl get clusterrolebinding monitoring -o jsonpath='{.roleRef.name} {.subjects[0].kind} {.subjects[0].name} {.subjects[0].namespace}'
check 2 "monitor can list pods in all namespaces" can_i "$SA" list pods
check "monitor can list nodes" can_i "$SA" list nodes
check "monitor cannot delete pods" cannot_i "$SA" delete pods
finish
