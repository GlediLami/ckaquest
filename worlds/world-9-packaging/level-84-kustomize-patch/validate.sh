#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
C="{.spec.template.spec.containers[0]"
cm_name() { jp kustomize-patch deploy/web "$C.envFrom[0].configMapRef.name}"; }
cm_ok() { local n; n="$(cm_name)"; [ -n "$n" ] && field_eq kustomize-patch "cm/$n" '{.data.MODE}' production; }
check 2 "web has memory limit 128Mi" field_eq kustomize-patch deploy/web "$C.resources.limits.memory}" 128Mi
check "web has CPU limit 200m" field_eq kustomize-patch deploy/web "$C.resources.limits.cpu}" 200m
check 2 "web loads a generated web-config with MODE=production" cm_ok
check "the ConfigMap name has the generator hash" out_match "^web-config-[a-z0-9]+$" cm_name
check "web is ready" deploy_ready kustomize-patch web
check "base is unchanged" sh -c '! grep -q limits "$CQ_WORK/84/base/deployment.yaml"'
finish
