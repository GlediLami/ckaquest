#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
check 2 "web-app runs the previous (v1) pod template" field_eq ckaquest deploy/web-app "{.spec.template.metadata.labels.version}" v1
check "web-app no longer uses the broken image" field_nomatch ckaquest deploy/web-app "{.spec.template.spec.containers[0].image}" nonexistent
check 2 "web-app has 2/2 ready replicas" deploy_ready ckaquest web-app 2
finish
