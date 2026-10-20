#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
check 3 "legacy.internal resolves to 10.10.10.10" out_match "10\.10\.10\.10" in_cluster_out dns-custom busybox:1.36 nslookup legacy.internal
check 2 "kubernetes.default still resolves" in_cluster_ok dns-custom busybox:1.36 nslookup kubernetes.default.svc.cluster.local
check "CoreDNS pods are Ready" pods_ready kube-system k8s-app=kube-dns
finish
