#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
same() { diff <(sed -e 's/[[:space:]]\+/ /g' -e 's/ $//' "$1" | sed '/^$/d') <(eval "$2" | sed -e 's/[[:space:]]\+/ /g' -e 's/ $//' | sed '/^$/d') >/dev/null 2>&1; }
same_sorted() { diff <(sed -e 's/[[:space:]]\+/ /g' -e 's/ $//' "$1" | sed '/^$/d' | sort) <(eval "$2" | sed -e 's/[[:space:]]\+/ /g' -e 's/ $//' | sed '/^$/d' | sort) >/dev/null 2>&1; }
EXP="kubectl get pods -A --field-selector=status.phase!=Running,status.phase!=Succeeded -o jsonpath='{range .items[*]}{.metadata.namespace}/{.metadata.name}{\"\\n\"}{end}' | grep -v '^kube-system/'"
check "broken.txt names drill-109/badimage" file_contains "$CQ_WORK/109/broken.txt" "^drill-109/badimage$"
check "broken.txt names drill-109b/toobig" file_contains "$CQ_WORK/109/broken.txt" "^drill-109b/toobig$"
check 2 "broken.txt has exactly the not-running pods" same_sorted "$CQ_WORK/109/broken.txt" "$EXP"
finish
