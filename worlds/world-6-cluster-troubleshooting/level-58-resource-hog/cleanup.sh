#!/usr/bin/env bash
kubectl delete namespace top-lab --ignore-not-found --wait=false >/dev/null 2>&1
