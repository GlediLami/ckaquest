#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
check 2 "app-stable has 9 ready replicas" deploy_ready ckaquest app-stable 9
check 2 "app-canary has 1 ready replica" deploy_ready ckaquest app-canary 1
finish
