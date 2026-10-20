#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
same() { diff <(sed -e 's/[[:space:]]\+/ /g' -e 's/ $//' "$1" | sed '/^$/d') <(eval "$2" | sed -e 's/[[:space:]]\+/ /g' -e 's/ $//' | sed '/^$/d') >/dev/null 2>&1; }
same_sorted() { diff <(sed -e 's/[[:space:]]\+/ /g' -e 's/ $//' "$1" | sed '/^$/d' | sort) <(eval "$2" | sed -e 's/[[:space:]]\+/ /g' -e 's/ $//' | sed '/^$/d' | sort) >/dev/null 2>&1; }
EXP="kubectl get pods -n drill-104 --sort-by=.metadata.name -o custom-columns=POD:.metadata.name,IMAGE:.spec.containers[0].image,NODE:.spec.nodeName"
check 3 "pods.txt matches the expected table" same "$CQ_WORK/104/pods.txt" "$EXP"
finish
