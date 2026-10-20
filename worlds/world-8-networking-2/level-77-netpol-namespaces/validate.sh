#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
T="nc -z -w 3 postgres.db-ns.svc.cluster.local 5432"
check "allow-frontend selects app=postgres" field_eq db-ns netpol/allow-frontend '{.spec.podSelector.matchLabels.app}' postgres
check 2 "a pod in frontend-ns can connect" in_cluster_ok frontend-ns busybox:1.36 $T
check 2 "a pod in other-ns is blocked" in_cluster_fails other-ns busybox:1.36 $T
check "a pod in db-ns itself is blocked" in_cluster_fails db-ns busybox:1.36 $T
finish
