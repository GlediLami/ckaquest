#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
F="$CQ_WORK/82/preview.yaml"
check "preview.yaml exists" file_exists "$F"
check 2 "it has replicas: 3" file_contains "$F" "replicas: 3"
check 2 "it has type: NodePort" file_contains "$F" "type: NodePort"
check "it is release preview with nginx:1.28-alpine" file_contains "$F" "preview-webapp"
check "nothing was installed" out_eq "" helm list -n helm-render -q
finish
