#!/usr/bin/env bash
source "$CQ_ROOT/lib/common.sh"
helm uninstall old-api -n helm-team-a
helm uninstall old-web -n helm-team-b
