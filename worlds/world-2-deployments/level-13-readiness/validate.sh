#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
P="{.spec.template.spec.containers[0].readinessProbe.httpGet"
check 2 "readiness probe is HTTP GET on /" field_eq readiness deploy/slow-startup-app "$P.path}" /
check "readiness probe uses port 80" field_eq readiness deploy/slow-startup-app "$P.port}" 80
check 2 "all replicas of slow-startup-app are ready" deploy_ready readiness slow-startup-app
finish
