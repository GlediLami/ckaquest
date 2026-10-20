#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
corefile() { kubectl -n kube-system get cm coredns -o jsonpath='{.data.Corefile}'; }
check "Corefile serves the cluster.local zone" out_match 'kubernetes cluster\.local in-addr\.arpa' corefile
check "CoreDNS pods are ready" pods_ready kube-system k8s-app=kube-dns
check 3 "web.dns-lab.svc.cluster.local resolves from a pod" in_cluster_ok dns-lab busybox:1.28 nslookup web.dns-lab.svc.cluster.local
finish
