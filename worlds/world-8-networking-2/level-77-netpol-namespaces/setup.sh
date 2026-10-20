#!/usr/bin/env bash
set -uo pipefail
source "$CQ_ROOT/lib/common.sh"
kubectl create namespace frontend-ns --dry-run=client -o yaml | kubectl apply -f - >/dev/null
kubectl create namespace other-ns --dry-run=client -o yaml | kubectl apply -f - >/dev/null
kubectl run postgres -n db-ns --image=postgres:16-alpine --labels=app=postgres --env=POSTGRES_PASSWORD=cq --port=5432 >/dev/null
kubectl expose pod postgres -n db-ns --port=5432 >/dev/null
kubectl wait --for=condition=Ready pod/postgres -n db-ns --timeout=120s >/dev/null
