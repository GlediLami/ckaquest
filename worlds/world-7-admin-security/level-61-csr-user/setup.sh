#!/usr/bin/env bash
set -uo pipefail
source "$CQ_ROOT/lib/common.sh"
W="$(cq_work_dir 61)"
[ -f "$W/jane.key" ] || openssl genrsa -out "$W/jane.key" 2048 2>/dev/null
openssl req -new -key "$W/jane.key" -subj "/CN=jane/O=dev" -out "$W/jane.csr" 2>/dev/null
mv -f "$W/jane.crt" "$W/jane.crt.old" 2>/dev/null || true
kubectl delete csr jane --ignore-not-found >/dev/null
