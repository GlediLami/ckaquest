#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
allows_one() { [ "$(jp ckaquest pdb/db-proxy-pdb "{.status.disruptionsAllowed}")" = 1 ]; }
keeps_two() { [ "$(jp ckaquest pdb/db-proxy-pdb "{.spec.minAvailable}")" = 2 ] || [ "$(jp ckaquest pdb/db-proxy-pdb "{.spec.maxUnavailable}")" = 1 ]; }
check 2 "db-proxy-pdb keeps 2 pods available" keeps_two
check "the PDB allows exactly 1 disruption" allows_one
check "database-proxy has 3/3 ready replicas" deploy_ready ckaquest database-proxy 3
finish
