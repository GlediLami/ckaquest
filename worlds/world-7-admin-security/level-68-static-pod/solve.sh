#!/usr/bin/env bash
source "$CQ_ROOT/lib/common.sh"
kubectl run static-web -n static-lab --image=nginx:1.27-alpine --port=80 --labels=app=static-web --dry-run=client -o yaml > /tmp/cq-static-web.yaml
cq_node_put node01 /tmp/cq-static-web.yaml /etc/kubernetes/manifests/static-web.yaml
cq_wait 90 kubectl get pod "static-web-$(cq_node_name node01)" -n static-lab
