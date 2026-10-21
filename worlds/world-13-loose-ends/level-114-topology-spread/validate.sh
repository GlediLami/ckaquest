#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
N1="$(cq_node_name node01)"; N2="$(cq_node_name node02)"
T='{.spec.template.spec.topologySpreadConstraints[0]'
per_node() { kubectl get pods -n spread-lab -l app=api -o jsonpath='{range .items[?(@.status.phase=="Running")]}{.spec.nodeName} {.metadata.deletionTimestamp}{"\n"}{end}' | awk 'NF==1{print $1}' | grep -cx "$1"; }
two_each() { [ "$(per_node "$N1")" = 2 ] && [ "$(per_node "$N2")" = 2 ]; }
check "node01 is in zone-a" field_eq - node/$N1 '{.metadata.labels.topology\.kubernetes\.io/zone}' zone-a
check "node02 is in zone-b" field_eq - node/$N2 '{.metadata.labels.topology\.kubernetes\.io/zone}' zone-b
check 2 "spread by zone with maxSkew 1" field_eq spread-lab deploy/api "$T.topologyKey}/$T.maxSkew}" topology.kubernetes.io/zone/1
check "whenUnsatisfiable is DoNotSchedule" field_eq spread-lab deploy/api "$T.whenUnsatisfiable}" DoNotSchedule
check "the constraint selects the api pods" field_match spread-lab deploy/api "$T.labelSelector}" api
check "node affinity is still there" field_match spread-lab deploy/api '{.spec.template.spec.affinity.nodeAffinity}' preferred
check "4 replicas ready" field_eq spread-lab deploy/api '{.spec.replicas}/{.status.readyReplicas}/{.status.updatedReplicas}' 4/4/4
check 2 "2 api pods in each zone" two_each
finish
