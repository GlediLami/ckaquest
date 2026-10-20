#!/usr/bin/env bash
source "$CQ_ROOT/lib/common.sh"
cq_restore_manifest kube-apiserver
cq_wait_api 240 || true
