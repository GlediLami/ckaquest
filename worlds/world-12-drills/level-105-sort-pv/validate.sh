#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
want="$(printf 'drill-pv-b\ndrill-pv-d\ndrill-pv-a\ndrill-pv-c')"
check 3 "pvs.txt lists b, d, a, c" out_eq "$want" sh -c "sed -e 's/[[:space:]]*$//' -e '/^$/d' '$CQ_WORK/105/pvs.txt'"
finish
