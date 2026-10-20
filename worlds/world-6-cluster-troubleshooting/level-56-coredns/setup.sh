#!/usr/bin/env bash
set -euo pipefail
source "$CQ_ROOT/lib/common.sh"
mkdir -p "$CQ_HOME/backup"
[ -f "$CQ_HOME/backup/Corefile" ] || kubectl -n kube-system get cm coredns -o jsonpath='{.data.Corefile}' > "$CQ_HOME/backup/Corefile"
kubectl create deployment web -n "$NAMESPACE" --image=nginx:1.27-alpine >/dev/null
kubectl expose deployment web -n "$NAMESPACE" --port=80 >/dev/null
sed 's|kubernetes cluster.local in-addr.arpa ip6.arpa|kubernetes cluster.locl in-addr.arpa ip6.arpa|' "$CQ_HOME/backup/Corefile" > "$CQ_HOME/backup/Corefile.broken"
kubectl -n kube-system create cm coredns --from-file=Corefile="$CQ_HOME/backup/Corefile.broken" --dry-run=client -o yaml | kubectl apply -f - >/dev/null
kubectl -n kube-system rollout restart deploy coredns >/dev/null
kubectl -n kube-system rollout status deploy coredns --timeout=120s >/dev/null
