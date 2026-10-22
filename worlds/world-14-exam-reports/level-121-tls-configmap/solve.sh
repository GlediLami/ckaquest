#!/usr/bin/env bash
source "$CQ_ROOT/lib/common.sh"
kubectl get cm nginx-tls -n tls-lab -o yaml | sed 's/ssl_protocols TLSv1.3;/ssl_protocols TLSv1.2 TLSv1.3;/' | kubectl apply -f - >/dev/null
kubectl patch cm nginx-tls -n tls-lab -p '{"immutable":true}' >/dev/null
kubectl rollout restart deploy/web -n tls-lab >/dev/null
kubectl rollout status deploy/web -n tls-lab --timeout=120s
