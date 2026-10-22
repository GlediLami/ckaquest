#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
F="$CQ_WORK/122/crds.txt"; S="$CQ_WORK/122/subject.txt"
all_listed() { local c; for c in $(kubectl get crd -o name | grep cert-manager.io | cut -d/ -f2); do grep -q "$c" "$F" || return 1; done; }
only_cm() { ! grep -v -e cert-manager -e '^NAME' "$F" | grep -q .; }
check "crds.txt exists" file_exists "$F"
check 2 "it lists every cert-manager CRD" all_listed
check "it lists nothing else" only_cm
check "subject.txt exists" file_exists "$S"
check 2 "subject.txt is the explain output for Certificate spec.subject" bash -c "grep -q 'KIND: *Certificate' '$S' && grep -qi 'FIELD: *subject' '$S' && grep -q 'organizations' '$S'" 
finish
