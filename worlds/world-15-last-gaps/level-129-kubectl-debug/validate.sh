#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
N1="$(cq_node_name node01)"
token() { jp debug-lab secret/api-token '{.data.token}' | base64 -d; }
node_dbg() { kubectl get pods -n debug-lab -o jsonpath='{range .items[*]}{.metadata.name} {.spec.nodeName}{"\n"}{end}' | grep -q "^node-debugger-.* $N1$"; }
check 2 "pod api has an ephemeral container targeting container api" field_eq debug-lab pod/api '{.spec.ephemeralContainers[0].targetContainerName}' api
check 2 "token.txt holds the API_TOKEN value" out_eq "$(token)" cat "$CQ_WORK/129/token.txt"
check "a node-debugger pod ran on node01" node_dbg
check 2 "staticpodpath.txt is /etc/kubernetes/manifests" out_eq /etc/kubernetes/manifests cat "$CQ_WORK/129/staticpodpath.txt" 
finish
