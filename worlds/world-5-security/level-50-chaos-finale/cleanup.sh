#!/usr/bin/env bash
kubectl taint node ckaquest-worker dedicated- >/dev/null 2>&1 || true
kubectl label node ckaquest-worker accelerator- >/dev/null 2>&1 || true
