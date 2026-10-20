#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
sts_ready() { [ "$(jp statefulset sts/database "{.status.readyReplicas}")" = 3 ]; }
check "StatefulSet database exists" exists statefulset sts/database
check "it uses database-service as serviceName" field_eq statefulset sts/database "{.spec.serviceName}" database-service
check 2 "3/3 replicas are ready" sts_ready
check "pods have stable names (database-0 exists)" pod_ready statefulset database-0
check "Deployment database is gone" not_exists statefulset deploy/database
finish
