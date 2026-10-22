#!/usr/bin/env bash
set -uo pipefail
source "$CQ_ROOT/lib/common.sh"
source "$CQ_ROOT/cluster/versions.env"
"$CQ_ROOT/bin/cq-helm-repo" ensure >/dev/null
helm uninstall argocd -n argocd >/dev/null 2>&1
helm repo remove argo >/dev/null 2>&1
W="$(cq_work_dir 117)"; [ -e "$W/argocd.yaml" ] && mv -f "$W/argocd.yaml" "$W/argocd.yaml.old"; true
# The CRDs come from the same chart, applied outside Helm like a platform team would
helm template crds "$CQ_HOME/helm-repo/argo-cd-$ARGOCD_CHART_VERSION.tgz" --set crds.install=true \
  | "$CQ_ROOT/venv/bin/python3" -c '
import sys, yaml
docs = [d for d in yaml.safe_load_all(sys.stdin) if d and d.get("kind") == "CustomResourceDefinition"]
print(yaml.safe_dump_all(docs))' | kubectl apply --server-side -f - >/dev/null
