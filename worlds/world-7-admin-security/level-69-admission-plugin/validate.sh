#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
check 2 "NamespaceAutoProvision is enabled" node_ok controlplane 'grep -- "--enable-admission-plugins=" /etc/kubernetes/manifests/kube-apiserver.yaml | grep -q NamespaceAutoProvision'
check "NodeRestriction is still enabled" node_ok controlplane 'grep -- "--enable-admission-plugins=" /etc/kubernetes/manifests/kube-apiserver.yaml | grep -q NodeRestriction'
check "API server answers" cq_api_up
check 2 "pod probe exists in auto-created" exists auto-created pod/probe
finish
