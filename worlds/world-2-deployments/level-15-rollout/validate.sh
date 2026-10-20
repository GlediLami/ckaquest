#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
check 2 "maxUnavailable is 1" field_eq ckaquest deploy/critical-api "{.spec.strategy.rollingUpdate.maxUnavailable}" 1
check "strategy is still RollingUpdate" field_eq ckaquest deploy/critical-api "{.spec.strategy.type}" RollingUpdate
check "critical-api has 3/3 ready replicas" deploy_ready ckaquest critical-api 3
finish
