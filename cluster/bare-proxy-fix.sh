#!/usr/bin/env bash
# Runs on a bare control-plane node (systemd unit from "cq-cluster bare-up").
# kube-proxy cannot set nf_conntrack_max inside a container. kind solves this with
# conntrack.maxPerCore: 0. This waits for the player's "kubeadm init" and applies the same.
export KUBECONFIG=/etc/kubernetes/admin.conf
while :; do
  if [ -f "$KUBECONFIG" ] && kubectl -n kube-system get cm kube-proxy >/dev/null 2>&1; then
    if kubectl -n kube-system get cm kube-proxy -o jsonpath='{.data.config\.conf}' | grep -q 'maxPerCore: null'; then
      kubectl -n kube-system get cm kube-proxy -o yaml | sed 's/maxPerCore: null/maxPerCore: 0/' | kubectl apply -f - >/dev/null 2>&1 \
        && kubectl -n kube-system rollout restart ds/kube-proxy >/dev/null 2>&1
    fi
  fi
  sleep 10
done
