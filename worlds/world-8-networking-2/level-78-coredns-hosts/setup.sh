#!/usr/bin/env bash
set -uo pipefail
source "$CQ_ROOT/lib/common.sh"
mkdir -p "$CQ_HOME/backup"
[ -f "$CQ_HOME/backup/coredns-78.yaml" ] || kubectl get cm coredns -n kube-system -o yaml > "$CQ_HOME/backup/coredns-78.yaml"
