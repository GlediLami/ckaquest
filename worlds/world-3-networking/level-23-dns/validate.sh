#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
answers() { kubectl logs app-client -n dns --tail=3 2>/dev/null | grep -q "accepting connections"; }
check "app-client points at database-service" field_match dns pod/app-client "{.spec.containers[0].command} {.spec.containers[0].args}" "database-service"
check 2 "app-client reaches the database (accepting connections)" answers
finish
