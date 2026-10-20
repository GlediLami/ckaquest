#!/usr/bin/env bash
kubectl delete namespace pss-lab --ignore-not-found --wait=false >/dev/null 2>&1
