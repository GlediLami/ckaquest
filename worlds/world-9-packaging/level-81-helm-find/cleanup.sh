#!/usr/bin/env bash
source "$CQ_ROOT/lib/common.sh"
for r in $(helm list -n helm-audit -aq 2>/dev/null); do helm uninstall "$r" -n helm-audit >/dev/null 2>&1; done
for r in $(helm list -n helm-team-a -aq 2>/dev/null); do helm uninstall "$r" -n helm-team-a >/dev/null 2>&1; done
for r in $(helm list -n helm-team-b -aq 2>/dev/null); do helm uninstall "$r" -n helm-team-b >/dev/null 2>&1; done
kubectl delete ns helm-team-a helm-team-b --ignore-not-found --wait=false >/dev/null 2>&1
true
