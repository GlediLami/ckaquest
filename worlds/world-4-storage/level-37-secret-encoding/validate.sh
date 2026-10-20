#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
decoded() { jp ckaquest secret/db-credentials "{.data.$1}" | base64 -d 2>/dev/null; }
pod_connected() { kubectl logs database-client -n ckaquest 2>/dev/null | grep -q "Connected successfully"; }
pod_user() { kubectl exec database-client -n ckaquest -- sh -c 'echo $DB_USER' 2>/dev/null; }
check 2 "secret username decodes to admin" out_eq admin decoded username
check "secret password decodes to secretpass123" out_eq secretpass123 decoded password
check "database-client is Running" pod_running ckaquest database-client
check "database-client logged 'Connected successfully'" pod_connected
check "the pod sees DB_USER=admin" out_eq admin pod_user
finish
