#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
same() { diff <(sed -e 's/[[:space:]]\+/ /g' -e 's/ $//' "$1" | sed '/^$/d') <(eval "$2" | sed -e 's/[[:space:]]\+/ /g' -e 's/ $//' | sed '/^$/d') >/dev/null 2>&1; }
same_sorted() { diff <(sed -e 's/[[:space:]]\+/ /g' -e 's/ $//' "$1" | sed '/^$/d' | sort) <(eval "$2" | sed -e 's/[[:space:]]\+/ /g' -e 's/ $//' | sed '/^$/d' | sort) >/dev/null 2>&1; }
EXP="kubectl get pods -n drill-108 -l app=shop -o jsonpath='{range .items[*]}{.metadata.name} {.spec.containers[?(@.name==\"sidecar\")].image}{\"\\n\"}{end}'"
check 3 "sidecars.txt lists every shop pod with its sidecar image" same_sorted "$CQ_WORK/108/sidecars.txt" "$EXP"
finish
