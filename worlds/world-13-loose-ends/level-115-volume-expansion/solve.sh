#!/usr/bin/env bash
source "$CQ_ROOT/lib/common.sh"
kubectl patch sc slow-local -p '{"allowVolumeExpansion":true}' >/dev/null
kubectl patch pvc data -n grow-lab -p '{"spec":{"resources":{"requests":{"storage":"2Gi"}}}}' >/dev/null
