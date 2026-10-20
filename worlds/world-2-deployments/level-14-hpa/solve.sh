#!/usr/bin/env bash
kubectl set resources deployment web-backend -n hpa --requests=cpu=100m
kubectl rollout status deployment web-backend -n hpa --timeout=90s
