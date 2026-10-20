#!/usr/bin/env bash
set -uo pipefail
source "$CQ_ROOT/lib/common.sh"
"$CQ_ROOT/bin/cq-helm-repo" ensure >/dev/null
for r in $(helm list -n helm-blog -aq 2>/dev/null); do helm uninstall "$r" -n helm-blog >/dev/null 2>&1; done
helm install blog webapp --repo http://127.0.0.1:8879 --version 1.0.0 -n helm-blog --wait >/dev/null
helm upgrade blog webapp --repo http://127.0.0.1:8879 --version 1.1.0 -n helm-blog --set replicaCount=2 >/dev/null
helm upgrade blog webapp --repo http://127.0.0.1:8879 --version 1.1.0 -n helm-blog --reuse-values --set image.tag=1.28-alpine-broken >/dev/null
