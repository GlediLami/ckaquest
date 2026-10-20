#!/usr/bin/env bash
# The quota comes from broken.yaml. The pod manifest goes to a file: applying it fails, that is the task.
source "$CQ_ROOT/lib/common.sh"
W="$(cq_work_dir 43)"
cp pod.yaml.tpl "$W/pod.yaml"
