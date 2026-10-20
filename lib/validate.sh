#!/usr/bin/env bash
# Validation helpers with exam-style partial scoring.
#
#   source "$CQ_ROOT/lib/validate.sh"
#   check "Deployment web has 3 ready replicas" deploy_ready web-ns web 3
#   check 2 "Pod uses the right image" field_eq web-ns pod/web '{.spec.containers[0].image}' nginx:1.27
#   finish
#
# check [weight] "description" command args...
# finish prints "SCORE got/total" and exits 0 only when every check passed.

source "$(dirname "${BASH_SOURCE[0]}")/common.sh"

_CQ_GOT=0
_CQ_TOTAL=0
_CQ_FAILED=0

check() {
  local weight=1
  if [[ "$1" =~ ^[0-9]+$ ]]; then weight="$1"; shift; fi
  local desc="$1"; shift
  _CQ_TOTAL=$((_CQ_TOTAL + weight))
  if "$@" >/dev/null 2>&1; then
    _CQ_GOT=$((_CQ_GOT + weight))
    echo "✅ $desc"
  else
    _CQ_FAILED=$((_CQ_FAILED + 1))
    echo "❌ $desc"
  fi
}

finish() {
  echo
  echo "SCORE ${_CQ_GOT}/${_CQ_TOTAL}"
  [ "$_CQ_FAILED" -eq 0 ]
  exit $?
}

# --- predicates (return 0/1, print nothing useful) ---

# jp <ns|-> <kind/name> <jsonpath>  -> prints the value ("-" = cluster scoped)
jp() {
  local ns="$1" obj="$2" path="$3"
  if [ "$ns" = "-" ]; then
    kubectl get "$obj" -o jsonpath="$path" 2>/dev/null
  else
    kubectl get "$obj" -n "$ns" -o jsonpath="$path" 2>/dev/null
  fi
}

exists() {
  local ns="$1" obj="$2"
  if [ "$ns" = "-" ]; then kubectl get "$obj"; else kubectl get "$obj" -n "$ns"; fi
}

not_exists() { ! exists "$@"; }

field_eq() { [ "$(jp "$1" "$2" "$3")" = "$4" ]; }
field_ne() { [ "$(jp "$1" "$2" "$3")" != "$4" ]; }
field_match() { jp "$1" "$2" "$3" | grep -Eq -- "$4"; }
field_nomatch() { ! jp "$1" "$2" "$3" | grep -Eq -- "$4"; }

pod_ready() {
  [ "$(jp "$1" "pod/$2" '{.status.conditions[?(@.type=="Ready")].status}')" = "True" ]
}

pod_running() { field_eq "$1" "pod/$2" '{.status.phase}' Running; }

# all pods matching a label selector are Ready (and at least one exists)
pods_ready() {
  local ns="$1" selector="$2"
  local states
  states="$(kubectl get pods -n "$ns" -l "$selector" -o jsonpath='{range .items[*]}{.status.conditions[?(@.type=="Ready")].status}{"\n"}{end}' 2>/dev/null)"
  [ -n "$states" ] && ! grep -qv True <<<"$states"
}

deploy_ready() {
  local ns="$1" name="$2" want="${3:-}"
  local ready spec
  ready="$(jp "$ns" "deploy/$name" '{.status.readyReplicas}')"
  spec="$(jp "$ns" "deploy/$name" '{.spec.replicas}')"
  [ -n "$ready" ] && [ "$ready" = "$spec" ] && { [ -z "$want" ] || [ "$ready" = "$want" ]; }
}

node_ready() {
  [ "$(jp - "node/$1" '{.status.conditions[?(@.type=="Ready")].status}')" = "True" ]
}

all_nodes_ready() {
  local states
  states="$(kubectl get nodes -o jsonpath='{range .items[*]}{.status.conditions[?(@.type=="Ready")].status}{"\n"}{end}')"
  [ -n "$states" ] && ! grep -qv True <<<"$states"
}

# can_i <as> <verb> <resource> [ns]   e.g. can_i john create pods development
can_i() {
  local as="$1" verb="$2" res="$3" ns="${4:-}"
  if [ -n "$ns" ]; then
    [ "$(kubectl auth can-i "$verb" "$res" --as="$as" -n "$ns" 2>/dev/null)" = "yes" ]
  else
    [ "$(kubectl auth can-i "$verb" "$res" --as="$as" 2>/dev/null)" = "yes" ]
  fi
}
cannot_i() { ! can_i "$@"; }

file_exists() { [ -s "$1" ]; }
file_contains() { grep -Eq -- "$2" "$1"; }
# file content equals text, ignoring surrounding whitespace and trailing newlines
file_eq() { [ "$(sed -e 's/[[:space:]]*$//' "$1" | sed -e '/^$/d')" = "$2" ]; }

# node_ok <node> <shell snippet>  -> runs on the node, success = exit 0
node_ok() { cq_node_sh "$1" "$2"; }

# command output equals: out_eq "expected" cmd args...
out_eq() { local want="$1"; shift; [ "$("$@" 2>/dev/null)" = "$want" ]; }
out_match() { local re="$1"; shift; "$@" 2>/dev/null | grep -Eq -- "$re"; }

# Run a throwaway pod and return its exit code: in_cluster_ok <ns> <image> <cmd...>
in_cluster_ok() {
  local ns="$1" image="$2"; shift 2
  local name="cq-probe-$RANDOM"
  kubectl run "$name" -n "$ns" --image="$image" --restart=Never --rm -i --quiet \
    --pod-running-timeout=60s --command -- "$@" >/dev/null 2>&1
}
in_cluster_fails() { ! in_cluster_ok "$@"; }
