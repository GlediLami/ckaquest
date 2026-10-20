#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
chart() { helm list -n helm-shop -o json | python3 -c 'import json,sys; print(" ".join(r["chart"] + ":" + r["status"] for r in json.load(sys.stdin) if r["name"] == "shop"))'; }
check "repo cq points at http://127.0.0.1:8879" out_match "^cq[[:space:]]+http://127.0.0.1:8879" helm repo list
check 2 "release shop runs chart webapp-1.0.0" out_eq "webapp-1.0.0:deployed" chart
check 2 "shop-webapp has 2/2 ready replicas" deploy_ready helm-shop shop-webapp 2
finish
