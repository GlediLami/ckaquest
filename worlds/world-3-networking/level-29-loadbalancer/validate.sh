#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
nodeport_answers() { cq_node_sh node01 "curl -s -o /dev/null -m 5 http://\$(hostname -i | cut -d\" \" -f1):30080"; }
check "web-service is type NodePort" field_eq ckaquest svc/web-service "{.spec.type}" NodePort
check 2 "nodePort is 30080" field_eq ckaquest svc/web-service "{.spec.ports[0].nodePort}" 30080
check 2 "node01:30080 answers" nodeport_answers
finish
