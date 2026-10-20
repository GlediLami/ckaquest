#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
check 3 "answers are pdb, networking.k8s.io, false" out_eq "$(printf 'pdb\nnetworking.k8s.io\nfalse')" sh -c "sed -e 's/[[:space:]]*$//' -e '/^$/d' '$CQ_WORK/110/answers.txt'"
finish
