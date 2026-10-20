#!/usr/bin/env bash
source "$CQ_ROOT/lib/common.sh"
if [ -f "$CQ_HOME/backup/Corefile" ]; then
  kubectl -n kube-system create cm coredns --from-file=Corefile="$CQ_HOME/backup/Corefile" --dry-run=client -o yaml | kubectl apply -f - >/dev/null
  kubectl -n kube-system rollout restart deploy coredns >/dev/null
  kubectl -n kube-system rollout status deploy coredns --timeout=120s >/dev/null || true
fi
