#!/usr/bin/env bash
source "$CQ_ROOT/lib/common.sh"
if [ -f "$CQ_HOME/backup/coredns-78.yaml" ]; then
  kubectl get cm coredns -n kube-system -o yaml | grep -q legacy.internal && {
    kubectl replace -f "$CQ_HOME/backup/coredns-78.yaml" >/dev/null 2>&1
    kubectl rollout restart deploy coredns -n kube-system >/dev/null 2>&1
  }
  mv -f "$CQ_HOME/backup/coredns-78.yaml" "$CQ_HOME/backup/coredns-78.yaml.done"
fi
true
