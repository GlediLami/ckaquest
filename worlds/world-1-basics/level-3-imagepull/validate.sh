#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
check "web-app uses an nginx image" field_match imagepull pod/web-app "{.spec.containers[0].image}" "^(docker.io/(library/)?)?nginx(:|@|$)"
check 2 "web-app is Ready" pod_ready imagepull web-app
finish
