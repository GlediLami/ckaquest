#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
check 2 "the server points at port 6443" node_ok controlplane 'grep -q "server: https://.*:6443" /root/.kube/config'
check 2 "current-context exists in the file" node_ok controlplane 'kubectl config get-contexts "$(kubectl config current-context)"'
check 2 "kubectl get nodes works on controlplane" node_ok controlplane 'kubectl get nodes'
finish
