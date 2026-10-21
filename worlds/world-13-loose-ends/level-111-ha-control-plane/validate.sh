#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
K='kubectl --kubeconfig /etc/kubernetes/admin.conf'
check "k8s-api.ckaquest.local is in /etc/hosts" node_ok bare-controlplane 'grep -Eq "^[0-9.]+[[:space:]]+k8s-api.ckaquest.local" /etc/hosts'
check "API server answers" node_ok bare-controlplane "$K get --raw=/readyz"
check 2 "controlPlaneEndpoint is k8s-api.ckaquest.local:6443" node_ok bare-controlplane "$K -n kube-system get cm kubeadm-config -o yaml | grep -q 'controlPlaneEndpoint: k8s-api.ckaquest.local:6443'"
check "podSubnet is 10.50.0.0/16" node_ok bare-controlplane "$K -n kube-system get cm kubeadm-config -o yaml | grep -q 'podSubnet: 10.50.0.0/16'"
check 2 "control plane certificates are uploaded (secret kubeadm-certs)" node_ok bare-controlplane "$K -n kube-system get secret kubeadm-certs"
check "admin.conf points at the endpoint, not the node IP" node_ok bare-controlplane 'grep -q "server: https://k8s-api.ckaquest.local:6443" /etc/kubernetes/admin.conf'
check "kubectl works for root without flags" node_ok bare-controlplane 'kubectl get nodes'
check 2 "cp-join.sh joins a control plane through the endpoint" node_ok bare-controlplane 'f=/root/cp-join.sh; grep -q "kubeadm join k8s-api.ckaquest.local:6443" $f && grep -q -- "--control-plane" $f && grep -Eq -- "--certificate-key [0-9a-f]{64}" $f && grep -q -- "--discovery-token-ca-cert-hash sha256:" $f'
finish
