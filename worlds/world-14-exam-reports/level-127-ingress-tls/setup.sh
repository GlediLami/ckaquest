#!/usr/bin/env bash
set -uo pipefail
source "$CQ_ROOT/lib/common.sh"
cert() { openssl req -x509 -newkey rsa:2048 -nodes -days 365 -subj "/CN=$2" -addext "subjectAltName=DNS:$2" -keyout "$1/tls.key" -out "$1/tls.crt" >/dev/null 2>&1; }
W="$(cq_work_dir 127)"
cert "$W" secure.example.com
kubectl create deployment app -n tls-ingress --image=hashicorp/http-echo:1.0 -- /http-echo -text="secure app" -listen=:5678 >/dev/null
kubectl expose deployment app -n tls-ingress --port=80 --target-port=5678 >/dev/null
