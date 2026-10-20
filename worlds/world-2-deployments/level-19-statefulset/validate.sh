#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
sts_ready() { [ "$(jp ckaquest sts/database "{.status.readyReplicas}")" = 3 ]; }
check "StatefulSet database exists" exists ckaquest sts/database
check "it uses database-service as serviceName" field_eq ckaquest sts/database "{.spec.serviceName}" database-service
check 2 "3/3 replicas are ready" sts_ready
check "pods have stable names (database-0 exists)" pod_ready ckaquest database-0
check "Deployment database is gone" not_exists ckaquest deploy/database
finish
