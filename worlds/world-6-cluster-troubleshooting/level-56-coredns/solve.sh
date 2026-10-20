#!/usr/bin/env bash
source "$CQ_ROOT/lib/common.sh"
kubectl -n kube-system get cm coredns -o yaml | sed 's|cluster.locl|cluster.local|' | kubectl apply -f -
kubectl -n kube-system rollout restart deploy coredns
kubectl -n kube-system rollout status deploy coredns --timeout=120s
