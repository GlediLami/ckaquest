#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
check 2 "API server on bare-controlplane answers" node_ok bare-controlplane 'kubectl --kubeconfig /etc/kubernetes/admin.conf get --raw=/readyz'
check 2 "podSubnet is 10.50.0.0/16" node_ok bare-controlplane 'kubectl --kubeconfig /etc/kubernetes/admin.conf -n kube-system get cm kubeadm-config -o yaml | grep -q "podSubnet: 10.50.0.0/16"'
check 2 "kubectl works for root without flags" node_ok bare-controlplane 'kubectl get nodes'
finish
