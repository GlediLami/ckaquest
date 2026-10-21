#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
A='{.spec.template.spec.affinity.podAntiAffinity.requiredDuringSchedulingIgnoredDuringExecution[0]'
running_nodes() { kubectl get pods -n anti-lab -l app=cache -o jsonpath='{range .items[?(@.status.phase=="Running")]}{.spec.nodeName}{"\n"}{end}'; }
two_nodes() { [ "$(running_nodes | wc -l)" = 2 ] && [ "$(running_nodes | sort -u | wc -l)" = 2 ]; }
one_pending() { [ "$(kubectl get pods -n anti-lab -l app=cache --field-selector=status.phase=Pending --no-headers 2>/dev/null | wc -l)" = 1 ]; }
check 2 "required anti-affinity with topologyKey kubernetes.io/hostname" field_eq anti-lab deploy/cache "$A.topologyKey}" kubernetes.io/hostname
check "the rule selects the cache pods" field_match anti-lab deploy/cache "$A.labelSelector}" cache
check "3 replicas, all from the updated template" field_eq anti-lab deploy/cache '{.spec.replicas}/{.status.updatedReplicas}' 3/3
check 2 "2 cache pods Running, on different nodes" two_nodes
check "the third pod is Pending" one_pending
finish
