#!/usr/bin/env bash
set -uo pipefail
source "$CQ_ROOT/lib/common.sh"
kubectl delete storageclass local-retain --ignore-not-found >/dev/null
