#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
SA=system:serviceaccount:monitoring:node-inspector
check "ClusterRole node-reader exists" exists - clusterrole/node-reader
check "ClusterRoleBinding node-inspector-binding uses node-reader" field_eq - clusterrolebinding/node-inspector-binding '{.roleRef.name}' node-reader
check 2 "node-inspector can list nodes" can_i "$SA" list nodes
check "node-inspector can watch nodes" can_i "$SA" watch nodes
check "node-inspector cannot delete nodes" cannot_i "$SA" delete nodes
check "node-inspector cannot list secrets anywhere" cannot_i "$SA" list secrets kube-system
finish
