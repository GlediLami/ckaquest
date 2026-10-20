#!/usr/bin/env bash
source "$CQ_ROOT/lib/common.sh"
kubectl patch httproute blog-route -n blog --type=json -p '[{"op":"replace","path":"/spec/parentRefs/0/name","value":"web-gw"},{"op":"replace","path":"/spec/rules/0/backendRefs/0/port","value":80}]'
