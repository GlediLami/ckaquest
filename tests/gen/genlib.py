"""Small writer for level folders. The generators in this folder call level() once per level.

Generated files are the source of truth after generation. Edit them directly; the
generators exist so a world can be written in one place and reviewed as a whole.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _block(text, indent="  "):
    return "".join((indent + line if line else "") + "\n" for line in text.strip("\n").split("\n"))


def _mission(m):
    out = []
    for key in ("name", "description", "objective"):
        out.append(f'{key}: "{m[key]}"\n')
    for key in ("xp", "difficulty", "expected_time", "domain", "course_section", "namespace"):
        out.append(f"{key}: {m[key]}\n")
    if m.get("requires"):
        out.append("requires:\n" + "".join(f"  - {r}\n" for r in m["requires"]))
    out.append("exam: true\n")
    out.append("concepts:\n" + "".join(f"  - {c}\n" for c in m["concepts"]))
    context = m.get("context", "kind-ckaquest")
    out.append("task: |\n" + _block(f"Context: `{context}`\n\n" + m["task"].strip()))
    out.append("docs:\n" + "".join(f"  - {d}\n" for d in m["docs"]))
    return "".join(out)


def _script(body, header):
    return f"#!/usr/bin/env bash\n{header}\n{body.strip()}\n"


def level(world, name, mission, setup=None, validate="", solve=None, cleanup=None,
          hints=(), solution="", debrief="", broken=None):
    d = ROOT / "worlds" / world / name
    d.mkdir(parents=True, exist_ok=True)
    (d / "mission.yaml").write_text(_mission(mission))
    common = 'source "$CQ_ROOT/lib/common.sh"'
    if setup:
        (d / "setup.sh").write_text(_script(setup, "set -uo pipefail\n" + common))
    if broken:
        (d / "broken.yaml").write_text(broken.strip() + "\n")
    (d / "validate.sh").write_text(_script(validate + "\nfinish", 'source "$CQ_ROOT/lib/validate.sh"'))
    if solve:
        (d / "solve.sh").write_text(_script(solve, common))
    if cleanup:
        (d / "cleanup.sh").write_text(_script(cleanup + "\ntrue", common))
    for i, h in enumerate(hints, 1):
        (d / f"hint-{i}.txt").write_text(h.strip() + "\n")
    (d / "solution.md").write_text(f"# Solution\n\n{solution.strip()}\n")
    (d / "debrief.md").write_text(debrief.strip() + "\n")
