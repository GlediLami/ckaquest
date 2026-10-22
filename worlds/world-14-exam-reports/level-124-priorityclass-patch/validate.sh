#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
want() { echo $(( $(kubectl get priorityclass -o jsonpath='{range .items[*]}{.metadata.name} {.value}{"\n"}{end}' | grep -v -e '^system-' -e '^high-priority ' | awk '{print $2}' | sort -n | tail -1) - 1 )); }
pod_prio() { kubectl get pods -n priority-lab -l app=busybox-logger --field-selector=status.phase=Running -o jsonpath='{.items[*].spec.priority}'; }
check 2 "high-priority is one less than the highest user-defined class" out_eq "$(want)" kubectl get priorityclass high-priority -o jsonpath='{.value}'
check 2 "busybox-logger uses high-priority" field_eq priority-lab deploy/busybox-logger '{.spec.template.spec.priorityClassName}' high-priority
check "its pod runs with that priority" out_eq "$(want)" pod_prio
finish
