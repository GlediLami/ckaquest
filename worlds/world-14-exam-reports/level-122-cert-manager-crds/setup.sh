#!/usr/bin/env bash
set -uo pipefail
source "$CQ_ROOT/lib/common.sh"
W="$(cq_work_dir 122)"; [ -e "$W/crds.txt" ] && mv -f "$W/crds.txt" "$W/crds.txt.old"; [ -e "$W/subject.txt" ] && mv -f "$W/subject.txt" "$W/subject.txt.old"; true
source "$CQ_ROOT/cluster/versions.env"
src="$CQ_HOME/offline/manifests/cert-manager.crds.yaml"
if [ -s "$src" ]; then kubectl apply --server-side -f "$src" >/dev/null
else kubectl apply --server-side -f "https://github.com/cert-manager/cert-manager/releases/download/$CERT_MANAGER_VERSION/cert-manager.crds.yaml" >/dev/null; fi
kubectl wait --for=condition=Established crd/certificates.cert-manager.io --timeout=60s >/dev/null
