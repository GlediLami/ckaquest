#!/usr/bin/env bash
source "$CQ_ROOT/lib/common.sh"
kubectl patch ingress docs-ingress -n ingress-lab -p '{"spec":{"ingressClassName":"nginx"}}'
sleep 15
