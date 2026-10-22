#!/usr/bin/env bash
source "$CQ_ROOT/lib/common.sh"
kubectl patch deploy app-logger -n logs-lab --type=strategic -p '{"spec":{"template":{"spec":{
 "volumes":[{"name":"logs","emptyDir":{}}],
 "containers":[
  {"name":"app","volumeMounts":[{"name":"logs","mountPath":"/var/log"}]},
  {"name":"sidecar","image":"busybox:1.36","command":["/bin/sh","-c","tail -n+1 -f /var/log/app.log"],"volumeMounts":[{"name":"logs","mountPath":"/var/log"}]}]}}}}'
kubectl rollout status deploy/app-logger -n logs-lab --timeout=120s
sleep 8
