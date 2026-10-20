#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
check "deny-all is still there" exists ckaquest netpol/deny-all
check 2 "backend reaches database:5432" kubectl exec -n ckaquest backend -- nc -z -w 3 database 5432
check 2 "a pod without app=backend cannot reach database:5432" in_cluster_fails ckaquest busybox:1.36 nc -z -w 3 database.ckaquest.svc.cluster.local 5432
finish
