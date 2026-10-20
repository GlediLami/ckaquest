#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
check "CRD backups.ops.example.com is Established" field_eq - crd/backups.ops.example.com '{.status.conditions[?(@.type=="Established")].status}' True
check 2 "Backup nightly has the right spec" out_eq "0 2 * * *|postgres|7" kubectl get backup nightly -n crd-lab -o jsonpath='{.spec.schedule}|{.spec.target}|{.spec.retain}'
check "shortname.txt says bk" file_eq "$CQ_WORK/85/shortname.txt" bk
finish
