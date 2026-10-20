#!/usr/bin/env bash
kubectl set resources deployment web-backend -n ckaquest --requests=cpu=100m
kubectl rollout status deployment web-backend -n ckaquest --timeout=90s
