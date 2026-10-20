#!/usr/bin/env bash
source "$CQ_ROOT/lib/common.sh"
helm repo add cq http://127.0.0.1:8879
helm repo update cq
helm install shop cq/webapp --version 1.0.0 -n helm-shop --set replicaCount=2 --wait
