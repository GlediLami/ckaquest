#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
check 2 "web-cluster is headless (clusterIP None)" field_eq ckaquest svc/web-cluster "{.spec.clusterIP}" None
check "selector is still app=web-cluster" field_eq ckaquest svc/web-cluster "{.spec.selector.app}" web-cluster
check 2 "web-0.web-cluster resolves" in_cluster_ok ckaquest busybox:1.36 nslookup web-0.web-cluster.ckaquest.svc.cluster.local
finish
