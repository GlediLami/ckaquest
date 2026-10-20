#!/usr/bin/env bash
source "$CQ_ROOT/lib/common.sh"
helm template preview webapp --repo http://127.0.0.1:8879 --version 1.1.0 --set replicaCount=3 --set service.type=NodePort > "$CQ_WORK/82/preview.yaml"
