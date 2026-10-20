#!/usr/bin/env bash
source "$CQ_ROOT/lib/common.sh"
cq_node_sh controlplane 'openssl x509 -in /etc/kubernetes/pki/apiserver.crt -noout -enddate > /opt/course/64/expiry-before.txt
sleep 1
kubeadm certs renew apiserver
mv /etc/kubernetes/manifests/kube-apiserver.yaml /root/
sleep 20
mv /root/kube-apiserver.yaml /etc/kubernetes/manifests/'
cq_wait_api 180
