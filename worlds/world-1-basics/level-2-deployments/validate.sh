#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
has_replicas() { [ "$(jp ckaquest deploy/web "{.spec.replicas}")" -ge 1 ]; }
check "web asks for at least 1 replica" has_replicas
check 2 "all replicas of web are ready" deploy_ready ckaquest web
finish
