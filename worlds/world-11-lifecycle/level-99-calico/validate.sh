#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
K='kubectl --kubeconfig /etc/kubernetes/admin.conf'
check 2 "Calico IP pool is 10.50.0.0/16" node_ok bare-controlplane "$K get ippools.crd.projectcalico.org default-ipv4-ippool -o jsonpath='{.spec.cidr}' | grep -qx 10.50.0.0/16"
check 2 "bare-controlplane is Ready" node_ok bare-controlplane "$K get node \$(hostname) --no-headers | grep -q ' Ready'"
check 2 "CoreDNS pods run with 10.50.x.x IPs" node_ok bare-controlplane "$K -n kube-system get pods -l k8s-app=kube-dns -o jsonpath='{.items[*].status.podIP}' | grep -q '^10\.50\.'"
finish
