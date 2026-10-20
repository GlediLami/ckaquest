#!/usr/bin/env bash
source "$CQ_ROOT/lib/common.sh"
cq_node_sh controlplane "sed -i 's|--enable-admission-plugins=NodeRestriction|--enable-admission-plugins=NodeRestriction,NamespaceAutoProvision|' /etc/kubernetes/manifests/kube-apiserver.yaml"
sleep 25
cq_wait_api 240
cq_wait 60 kubectl run probe -n auto-created --image=busybox:1.36 -- sleep 3600
