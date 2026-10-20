#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
nodeport_answers() { local ip; ip="$(kubectl get node "$(cq_node_name node01)" -o jsonpath='{.status.addresses[?(@.type=="InternalIP")].address}' | tr ' ' '\n' | grep -v : | head -1)"; cq_node_sh node01 "curl -s -o /dev/null -m 5 http://$ip:30080"; }
check "web-service is type NodePort" field_eq ckaquest svc/web-service "{.spec.type}" NodePort
check 2 "nodePort is 30080" field_eq ckaquest svc/web-service "{.spec.ports[0].nodePort}" 30080
check 2 "node01:30080 answers" nodeport_answers
finish
