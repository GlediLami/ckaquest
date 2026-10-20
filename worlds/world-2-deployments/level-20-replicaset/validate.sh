#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
owned() { [ "$(kubectl get rs -n replicaset -l app=webapp -o jsonpath="{.items[*].metadata.ownerReferences[0].kind}" | tr " " "\n" | sort -u)" = Deployment ]; }
check "Deployment web-app exists" exists replicaset deploy/web-app
check 2 "web-app has 3/3 ready replicas" deploy_ready replicaset web-app 3
check "ReplicaSet web-app-rs is gone" not_exists replicaset rs/web-app-rs
check "every ReplicaSet for app=webapp is owned by a Deployment" owned
finish
