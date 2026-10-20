#!/usr/bin/env bash
sed -e 's/cpu: "2500m"/cpu: "500m"/' -e 's/cpu: "3"/cpu: "1"/' -e 's/memory: "1Gi"/memory: "512Mi"/' -e 's/memory: "2Gi"/memory: "1Gi"/' \
  "$CQ_WORK/43/pod.yaml" | kubectl apply -f -
