#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
same() { diff <(sed -e 's/[[:space:]]\+/ /g' -e 's/ $//' "$1" | sed '/^$/d') <(eval "$2" | sed -e 's/[[:space:]]\+/ /g' -e 's/ $//' | sed '/^$/d') >/dev/null 2>&1; }
same_sorted() { diff <(sed -e 's/[[:space:]]\+/ /g' -e 's/ $//' "$1" | sed '/^$/d' | sort) <(eval "$2" | sed -e 's/[[:space:]]\+/ /g' -e 's/ $//' | sed '/^$/d' | sort) >/dev/null 2>&1; }
EXP="kubectl get nodes -o jsonpath='{range .items[*]}{.metadata.name} {.status.addresses[?(@.type==\"InternalIP\")].address}{\"\\n\"}{end}'"
check 3 "nodes.txt has name and InternalIP for every node" same_sorted "$CQ_WORK/103/nodes.txt" "$EXP"
finish
