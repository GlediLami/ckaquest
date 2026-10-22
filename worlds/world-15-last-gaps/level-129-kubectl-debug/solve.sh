#!/usr/bin/env bash
source "$CQ_ROOT/lib/common.sh"
kubectl debug api -n debug-lab --image=busybox:1.36 --target=api -c dbg -- sleep 3600 >/dev/null
running() { kubectl get pod api -n debug-lab -o jsonpath='{.status.ephemeralContainerStatuses[0].state.running}' | grep -q .; }
cq_wait 90 running
kubectl exec api -n debug-lab -c dbg -- sh -c 'tr "\0" "\n" < /proc/1/environ' | sed -n 's/^API_TOKEN=//p' > "$CQ_WORK/129/token.txt"
N1="$(cq_node_name node01)"
pod="$(kubectl debug "node/$N1" -n debug-lab --image=busybox:1.36 -- cat /host/var/lib/kubelet/config.yaml | sed -n 's/.*pod\/\([^ ]*\).*/\1/p' | head -1)"
[ -n "$pod" ] || pod="$(kubectl get pods -n debug-lab -o name | grep node-debugger | head -1 | cut -d/ -f2)"
done_() { kubectl get pod "$pod" -n debug-lab -o jsonpath='{.status.phase}' | grep -q Succeeded; }
cq_wait 90 done_
kubectl logs "$pod" -n debug-lab | sed -n 's/^staticPodPath: *//p' > "$CQ_WORK/129/staticpodpath.txt"
