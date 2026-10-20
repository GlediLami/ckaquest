#!/usr/bin/env bash
# Level test harness. For each level:
#   1. deploy it like the engine does (cleanup, namespace, setup.sh or broken.yaml)
#   2. validate.sh must FAIL on the broken state
#   3. apply the reference fix (solve.sh, else solution.yaml)
#   4. validate.sh must PASS within the timeout
#   5. cleanup.sh
#
# Usage: tests/run-levels.sh [filter]      e.g. tests/run-levels.sh level-5   or  world-6
# Env:   PASS_TIMEOUT (default 180s), KEEP=1 to skip cleanup of the last level
set -uo pipefail
source "$(dirname "$0")/../lib/common.sh"

FILTER="${1:-}"
PASS_TIMEOUT="${PASS_TIMEOUT:-180}"
RESULTS="$CQ_HOME/test-results.txt"
: > "$RESULTS"

is_protected() {
  case "$1" in ckaquest|default|kube-system|kube-public|kube-node-lease|local-path-storage|ingress-nginx|nginx-gateway) return 0 ;; esac
  return 1
}

level_requires() {
  awk '/^requires:/ {r=1; next} r && /^  - / {print $2; next} r {exit}' "$1/mission.yaml"
}

level_ns() {
  local ns
  ns="$(awk -F': *' '/^namespace:/ {print $2; exit}' "$1/mission.yaml" | tr -d '"')"
  echo "${ns:-ckaquest}"
}

run_in() { (cd "$1" && NAMESPACE="$2" PATH="$CQ_ROOT/bin/shims:$CQ_ROOT/bin:$PATH" bash "$3"); }

reset_default_ns() {
  kubectl label namespace ckaquest pod-security.kubernetes.io/enforce- pod-security.kubernetes.io/audit- \
    pod-security.kubernetes.io/warn- >/dev/null 2>&1
  kubectl delete all,cm,secret,pvc,netpol,ing,role,rolebinding,sa,quota,limits,hpa,pdb \
    --all -n ckaquest --ignore-not-found --timeout=90s >/dev/null 2>&1
}

apply_fix() {
  local dir="$1" ns="$2"
  if [ -f "$dir/solve.sh" ]; then
    run_in "$dir" "$ns" solve.sh
  elif [ -f "$dir/solution.yaml" ]; then
    kubectl apply -f "$dir/solution.yaml" >/dev/null 2>&1 \
      || kubectl replace --force -f "$dir/solution.yaml" >/dev/null
  else
    echo "no solve.sh or solution.yaml"; return 1
  fi
}

test_level() {
  local dir="$1" name ns out
  name="$(basename "$dir")"
  ns="$(level_ns "$dir")"
  printf '%-45s ' "$name"

  local addon
  for addon in $(level_requires "$dir"); do
    "$CQ_ROOT/bin/cq-cluster" addon "$addon" >/dev/null 2>&1 || { echo "ADDON-FAIL $addon"; echo "$name ADDON-FAIL" >> "$RESULTS"; return; }
  done
  [ -f "$dir/cleanup.sh" ] && run_in "$dir" "$ns" cleanup.sh >/dev/null 2>&1
  if is_protected "$ns"; then
    kubectl create namespace "$ns" >/dev/null 2>&1
    reset_default_ns
  else
    kubectl delete namespace "$ns" --ignore-not-found --timeout=120s >/dev/null 2>&1
    kubectl create namespace "$ns" >/dev/null 2>&1
  fi

  if [ -f "$dir/setup.sh" ]; then
    out="$(run_in "$dir" "$ns" setup.sh 2>&1)" || { echo "SETUP-FAIL"; echo "$name SETUP-FAIL" >> "$RESULTS"; echo "$out" | tail -5 | sed 's/^/    /'; return; }
  fi
  if [ -f "$dir/broken.yaml" ]; then
    out="$(kubectl apply -f "$dir/broken.yaml" 2>&1)" || { echo "SETUP-FAIL"; echo "$name SETUP-FAIL" >> "$RESULTS"; echo "$out" | tail -5 | sed 's/^/    /'; return; }
  fi
  sleep "${BROKEN_WAIT:-8}"

  if run_in "$dir" "$ns" validate.sh >/dev/null 2>&1; then
    echo -n "BROKEN-PASSES "
    echo "$name BROKEN-PASSES" >> "$RESULTS"
  fi

  out="$(apply_fix "$dir" "$ns" 2>&1)" || { echo "FIX-FAIL"; echo "$name FIX-FAIL" >> "$RESULTS"; echo "$out" | tail -5 | sed 's/^/    /'; }

  local end=$((SECONDS + PASS_TIMEOUT)) ok=false
  while [ "$SECONDS" -lt "$end" ]; do
    if out="$(run_in "$dir" "$ns" validate.sh 2>&1)"; then ok=true; break; fi
    sleep 5
  done
  if $ok; then
    echo "OK"
    echo "$name OK" >> "$RESULTS"
  else
    echo "FIXED-FAILS"
    echo "$name FIXED-FAILS" >> "$RESULTS"
    echo "$out" | grep -E "❌|SCORE|rror" | head -6 | sed 's/^/    /'
  fi

  if [ -z "${KEEP:-}" ]; then
    [ -f "$dir/cleanup.sh" ] && run_in "$dir" "$ns" cleanup.sh >/dev/null 2>&1
    is_protected "$ns" || kubectl delete namespace "$ns" --ignore-not-found --wait=false >/dev/null 2>&1
  fi
}

for dir in $(find "$CQ_ROOT/worlds" -mindepth 2 -maxdepth 2 -type d -name 'level-*' | sort -V); do
  case "$dir" in *"$FILTER"*) test_level "$dir" ;; esac
done

echo
grep -c " OK$" "$RESULTS" | xargs echo "passed:"
grep -v " OK$" "$RESULTS" || true
