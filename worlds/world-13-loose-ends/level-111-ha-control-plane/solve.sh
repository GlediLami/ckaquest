#!/usr/bin/env bash
source "$CQ_ROOT/lib/common.sh"
ip="$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}} {{end}}' "$(cq_node_name bare-controlplane)" | awk '{print $1}')"
cq_node_sh bare-controlplane "echo '$ip k8s-api.ckaquest.local' >> /etc/hosts
kubeadm init --control-plane-endpoint=k8s-api.ckaquest.local:6443 --pod-network-cidr=10.50.0.0/16 --upload-certs >/root/kubeadm-init.log 2>&1
mkdir -p /root/.kube && cp /etc/kubernetes/admin.conf /root/.kube/config
key=\$(kubeadm init phase upload-certs --upload-certs 2>/dev/null | tail -1)
kubeadm token create --print-join-command --certificate-key \$key > /root/cp-join.sh"
