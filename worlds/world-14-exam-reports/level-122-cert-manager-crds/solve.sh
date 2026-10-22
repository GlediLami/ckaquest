#!/usr/bin/env bash
source "$CQ_ROOT/lib/common.sh"
kubectl get crd | grep cert-manager > "$CQ_WORK/122/crds.txt"
kubectl explain certificate.spec.subject > "$CQ_WORK/122/subject.txt"
