"""Writes exam/sets/A.yaml to J.yaml from the exam layout in engine/exam.py (BLUEPRINT).

    venv/bin/python3 tests/gen/mock_sets.py

Rules: one level per blueprint slot, no conflicts, one install task on cluster3, the classic swap
(upgrade, etcd, certs) in sets C, F and I, and as many pool levels covered as possible.
Every task has the same weight.
"""
import random
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "engine"))
import exam  # noqa: E402

NAMES = "ABCDEFGHIJ"
CLASSIC_SETS = set("CFI")
MUST = {120}        # reported often, must be in at least one set


def build(seed):
    rng = random.Random(seed)
    used, sets = set(), []
    pool_all = {n for _, p in exam.BLUEPRINT for n in p} | set(exam.CLASSIC)
    for name in NAMES:
        picked = exam.blueprint_set(rng, classic=name in CLASSIC_SETS, prefer=pool_all - used)
        used |= set(picked)
        sets.append((name, picked))
    if not MUST <= used:
        return None
    return sets, pool_all - used


def main():
    levels = exam.all_levels()
    missions = {n: exam.load_mission(d) for n, d in levels.items()}
    best = None
    for seed in range(300):
        r = build(seed)
        if r and (best is None or len(r[1]) < len(best[1])):
            best = r
    sets, missing = best
    for name, picked in sets:
        install = next(n for n in picked if n in exam.BARE)
        classic = next((n for n in picked if n in exam.CLASSIC), None)
        extra = f", classic task {missions[classic]['name']}" if name in CLASSIC_SETS and classic else ""
        desc = f"Exam layout. Install task on cluster3: {missions[install]['name']}{extra}"
        weight = round(100 / len(picked), 1)
        Path(ROOT / "exam" / "sets" / f"{name}.yaml").write_text(yaml.safe_dump(
            {"name": name, "description": desc, "minutes": 120,
             "tasks": [{"level": n, "weight": weight} for n in picked]}, sort_keys=False))
        print(f"{name}  conflicts {exam.conflicts(picked)}  {picked}")
    print("pool levels in no set:", sorted(missing))


if __name__ == "__main__":
    main()
