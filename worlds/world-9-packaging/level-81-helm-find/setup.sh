#!/usr/bin/env bash
set -uo pipefail
source "$CQ_ROOT/lib/common.sh"
"$CQ_ROOT/bin/cq-helm-repo" ensure >/dev/null
for ns in helm-audit helm-team-a helm-team-b; do kubectl create ns $ns --dry-run=client -o yaml | kubectl apply -f - >/dev/null; done
for r in $(helm list -n helm-audit -aq 2>/dev/null); do helm uninstall "$r" -n helm-audit >/dev/null 2>&1; done
for r in $(helm list -n helm-team-a -aq 2>/dev/null); do helm uninstall "$r" -n helm-team-a >/dev/null 2>&1; done
for r in $(helm list -n helm-team-b -aq 2>/dev/null); do helm uninstall "$r" -n helm-team-b >/dev/null 2>&1; done
helm install old-api webapp --repo http://127.0.0.1:8879 --version 1.0.0 -n helm-team-a >/dev/null
helm install new-api webapp --repo http://127.0.0.1:8879 --version 1.1.0 -n helm-team-a >/dev/null
helm install old-web webapp --repo http://127.0.0.1:8879 --version 1.0.0 -n helm-team-b >/dev/null
helm install portal webapp --repo http://127.0.0.1:8879 --version 1.1.0 -n helm-audit >/dev/null
