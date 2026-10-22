#!/usr/bin/env bash
# End-to-end check of the exam simulator: start a small set, grade it unsolved (low score),
# apply every reference fix, grade again (100%), end it.
#   tests/exam-smoke.sh [set.yaml]      default: tests/sets/smoke.yaml
set -uo pipefail
cd "$(dirname "$0")/.." || exit 1
source lib/common.sh
./exam.sh start "${1:-tests/sets/smoke.yaml}" || exit 1
./exam.sh task 1 | head -5
./exam.sh grade | tail -4
for path in $(venv/bin/python3 -c 'import json; [print(t["path"]) for t in json.load(open("'"$CQ_HOME"'/exam/state.json"))["tasks"]]'); do
  ns="$(awk -F': *' '/^namespace:/ {print $2; exit}' "$path/mission.yaml")"
  if [ -f "$path/solve.sh" ]; then (cd "$path" && NAMESPACE="$ns" bash solve.sh >/dev/null 2>&1)
  else kubectl apply -f "$path/solution.yaml" >/dev/null 2>&1 || kubectl replace --force -f "$path/solution.yaml" >/dev/null 2>&1; fi
done
sleep 30
# a second grade on the same exam re-scores it
venv/bin/python3 - <<PY
import json, pathlib
p = pathlib.Path("$CQ_HOME/exam/state.json"); s = json.loads(p.read_text()); s.pop("graded_at", None); p.write_text(json.dumps(s))
PY
./exam.sh grade | tail -4
./exam.sh end
