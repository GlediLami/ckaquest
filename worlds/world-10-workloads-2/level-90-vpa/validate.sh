#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
P='{.spec.resourcePolicy.containerPolicies[0]'
check "targets Deployment api" out_eq "Deployment api" kubectl get vpa api-vpa -n vpa-lab -o jsonpath='{.spec.targetRef.kind} {.spec.targetRef.name}'
check 2 "updateMode is Off" field_eq vpa-lab vpa/api-vpa '{.spec.updatePolicy.updateMode}' Off
check "policy applies to all containers (*)" field_eq vpa-lab vpa/api-vpa "$P.containerName}" "*"
check 2 "minAllowed 25m / 32Mi" out_eq "25m 32Mi" kubectl get vpa api-vpa -n vpa-lab -o jsonpath="$P.minAllowed.cpu} $P.minAllowed.memory}"
check 2 "maxAllowed 500m / 256Mi" out_eq "500m 256Mi" kubectl get vpa api-vpa -n vpa-lab -o jsonpath="$P.maxAllowed.cpu} $P.maxAllowed.memory}"
finish
