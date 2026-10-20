#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
check "web-app has 3/3 ready replicas" deploy_ready poddisruptionbudget web-app 3
check 2 "web-pdb keeps 2 pods available" field_eq poddisruptionbudget pdb/web-pdb "{.spec.minAvailable}" 2
check "the PDB allows 1 disruption" field_eq poddisruptionbudget pdb/web-pdb "{.status.disruptionsAllowed}" 1
finish
