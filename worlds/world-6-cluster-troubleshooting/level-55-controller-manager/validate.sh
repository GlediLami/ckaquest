#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
check 2 "kube-controller-manager pod is Ready" pod_ready kube-system kube-controller-manager-ckaquest-control-plane
check "controller manager uses /etc/kubernetes/controller-manager.conf" node_ok controlplane 'grep -q -- "--kubeconfig=/etc/kubernetes/controller-manager.conf" /etc/kubernetes/manifests/kube-controller-manager.yaml'
check 2 "deployment api has 3 ready pods" deploy_ready cm-lab api 3
finish
