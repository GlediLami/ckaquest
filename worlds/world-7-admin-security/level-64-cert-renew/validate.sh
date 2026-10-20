#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
orig() { cq_node_sh controlplane 'cat /root/.cq-backup/64-enddate'; }
answer_ok() { [ "$(cq_node_sh controlplane 'cat /opt/course/64/expiry-before.txt' 2>/dev/null | tr -d '[:space:]')" = "$(orig | tr -d '[:space:]')" ]; }
renewed() { [ "$(cq_node_sh controlplane 'openssl x509 -in /etc/kubernetes/pki/apiserver.crt -noout -enddate')" != "$(orig)" ]; }
served() { cq_node_sh controlplane '[ "$(openssl x509 -in /etc/kubernetes/pki/apiserver.crt -noout -serial)" = "$(echo | openssl s_client -connect 127.0.0.1:6443 2>/dev/null | openssl x509 -noout -serial)" ]'; }
check 2 "expiry-before.txt has the old notAfter line" answer_ok
check 2 "apiserver.crt was renewed" renewed
check 2 "the API server serves the renewed certificate" served
check "API server answers" cq_api_up
finish
