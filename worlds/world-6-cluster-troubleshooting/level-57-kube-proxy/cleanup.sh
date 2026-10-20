#!/usr/bin/env bash
kubectl -n kube-system patch ds kube-proxy --type=json \
  -p '[{"op":"replace","path":"/spec/template/spec/containers/0/command/1","value":"--config=/var/lib/kube-proxy/config.conf"}]' >/dev/null 2>&1
kubectl -n kube-system rollout status ds kube-proxy --timeout=180s >/dev/null 2>&1 || true
