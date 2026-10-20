#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
last() { helm history blog -n helm-blog -o json | python3 -c 'import json,sys; h=json.load(sys.stdin)[-1]; print(h["status"], h["description"])'; }
check 2 "the latest revision is a rollback to revision 2" out_match "deployed Rollback to 2" last
check "blog runs the 1.28-alpine image" field_eq helm-blog deploy/blog-webapp '{.spec.template.spec.containers[0].image}' nginx:1.28-alpine
check 2 "blog-webapp has 2/2 ready replicas" deploy_ready helm-blog blog-webapp 2
finish
