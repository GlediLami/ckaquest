#!/usr/bin/env bash
source "$CQ_ROOT/lib/common.sh"
kubectl get cm coredns -n kube-system -o jsonpath='{.data.Corefile}' > /tmp/cq-corefile
python3 - <<'EOF'
p = "/tmp/cq-corefile"
s = open(p).read()
s = s.replace("    kubernetes cluster.local", "    hosts {\n       10.10.10.10 legacy.internal\n       fallthrough\n    }\n    kubernetes cluster.local", 1)
open(p, "w").write(s)
EOF
kubectl create cm coredns -n kube-system --from-file=Corefile=/tmp/cq-corefile --dry-run=client -o yaml | kubectl apply -f -
kubectl rollout restart deploy coredns -n kube-system
kubectl rollout status deploy coredns -n kube-system --timeout=90s
