#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
via_controller() { in_cluster_out ingress-lab curlimages/curl:8.11.1 curl -s -m 5 -H "Host: docs.example.com" http://ingress-nginx-controller.ingress-nginx/; }
check 2 "ingressClassName is nginx" field_eq ingress-lab ing/docs-ingress '{.spec.ingressClassName}' nginx
check 3 "docs.example.com through the controller answers 'docs site'" out_match "docs site" via_controller
finish
