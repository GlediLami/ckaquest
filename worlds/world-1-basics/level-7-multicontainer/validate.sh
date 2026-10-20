#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
two_ready() { [ "$(jp ckaquest pod/app-with-logging "{.status.containerStatuses[*].ready}")" = "true true" ]; }
check 2 "both containers of app-with-logging are ready" two_ready
check "app-with-logging is Ready" pod_ready ckaquest app-with-logging
finish
