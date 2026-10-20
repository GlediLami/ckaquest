#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
approved() { kubectl get csr jane -o jsonpath='{.status.conditions[?(@.type=="Approved")].status}' | grep -q True; }
crt_is_jane() { openssl x509 -in "$CQ_WORK/61/jane.crt" -noout -subject 2>/dev/null | grep -q "CN *= *jane"; }
crt_matches_key() { [ "$(openssl x509 -in "$CQ_WORK/61/jane.crt" -noout -pubkey 2>/dev/null)" = "$(openssl pkey -in "$CQ_WORK/61/jane.key" -pubout 2>/dev/null)" ]; }
check "CSR jane uses signer kube-apiserver-client" field_eq - csr/jane '{.spec.signerName}' kubernetes.io/kube-apiserver-client
check 2 "CSR jane is approved and issued" approved
check 2 "jane.crt is a PEM cert for CN=jane" crt_is_jane
check "jane.crt belongs to jane.key" crt_matches_key
check 2 "jane can list pods in dev-team" can_i jane list pods dev-team
check "jane cannot delete pods in dev-team" cannot_i jane delete pods dev-team
check "jane cannot list pods in default" cannot_i jane list pods default
finish
