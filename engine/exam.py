#!/usr/bin/env python3
"""CKAQuest exam simulator.

A mock exam is a list of campaign levels used as exam tasks: no hints, one 2-hour timer,
weighted scoring, pass mark 66%. cluster1 is the game cluster, cluster2 the lab cluster.

    exam.sh list                 available mock sets
    exam.sh start <set|random>   set up every task and start the timer
    exam.sh                      task list with time left (same as: exam.sh tasks)
    exam.sh task <n>             show one task
    exam.sh flag <n>             flag or unflag a task for review
    exam.sh time                 time left
    exam.sh grade                score every task, end the timer
    exam.sh review               solutions for every task (after grading)
    exam.sh end                  clean up all tasks
    exam.sh history              past results
"""
import json
import os
import random
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import yaml
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

CQ_ROOT = Path(__file__).resolve().parent.parent
CQ_HOME = Path(os.environ.get("CQ_HOME", Path.home() / ".ckaquest"))
EXAM_DIR = CQ_HOME / "exam"
STATE = EXAM_DIR / "state.json"
HISTORY = EXAM_DIR / "history.json"
SETS = CQ_ROOT / "exam" / "sets"
os.environ.setdefault("KUBECONFIG", os.environ.get("CKAQUEST_KUBECONFIG", str(CQ_HOME / "kubeconfig")))

console = Console()

DOMAIN_WEIGHTS = {"troubleshooting": 30, "architecture": 25, "networking": 20, "workloads": 15, "storage": 10}
DOMAIN_COUNTS = {"troubleshooting": 5, "architecture": 4, "networking": 3, "workloads": 3, "storage": 2}
PASS_MARK = 66
PROTECTED = {"ckaquest", "default", "kube-system", "kube-public", "kube-node-lease", "local-path-storage",
             "ingress-nginx", "nginx-gateway"}

# What a level changes outside its namespace. Two tasks with the same key never go in one set.
TOUCHES = {
    51: "kubelet-node01", 60: "kubelet-node01", 68: "kubelet-node01",
    52: "node02", 59: "node02",
    53: "control-plane", 54: "control-plane", 55: "control-plane", 64: "control-plane",
    66: "control-plane", 69: "control-plane", 67: "cp-kubeconfig",
    56: "coredns", 78: "coredns", 57: "kube-proxy",
    45: "node-labels", 46: "node-taints", 50: "node-taints", 94: "default-sc",
    101: "lab", 102: "lab",
}
# Setups that leave part of the cluster broken run last, so other setups still work.
DISRUPTIVE = {51, 52, 53, 54, 55, 56, 57, 60}
# Never in an exam: separate machines, or drills that are not exam tasks.
EXCLUDED = set(range(97, 101)) | set(range(103, 111))


def level_number(path):
    m = re.search(r"level-(\d+)", str(path))
    return int(m.group(1)) if m else 0


def all_levels():
    out = {}
    for d in sorted((CQ_ROOT / "worlds").glob("world-*/level-*")):
        out[level_number(d)] = d
    return out


def load_mission(d):
    with open(d / "mission.yaml") as f:
        return yaml.safe_load(f)


def script_env(mission):
    env = dict(os.environ)
    env.update(CQ_ROOT=str(CQ_ROOT), NAMESPACE=mission.get("namespace", "ckaquest"))
    env["PATH"] = f"{CQ_ROOT}/bin/shims:{CQ_ROOT}/bin:{env['PATH']}"
    return env


def run(d, name, mission, timeout=900):
    if not (d / name).exists():
        return None
    return subprocess.run(["bash", name], cwd=d, capture_output=True, text=True,
                          errors="replace", env=script_env(mission), timeout=timeout)


def load_state():
    if STATE.exists():
        return json.loads(STATE.read_text())
    return None


def save_state(state):
    EXAM_DIR.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(state, indent=2))


def exam_text(text):
    """Campaign wording to exam wording: named contexts and exam node names."""
    text = re.sub(r"Context: `kind-ckaquest-lab`", "Context: `kubectl config use-context cluster2`", text)
    text = re.sub(r"Context: `kind-ckaquest`", "Context: `kubectl config use-context cluster1`", text)
    text = text.replace("--context kind-ckaquest-lab", "--context cluster2")
    text = text.replace("lab-controlplane", "cluster2-controlplane").replace("lab-node01", "cluster2-node01")
    return text


def ensure_contexts():
    for name, kind_ctx in (("cluster1", "kind-ckaquest"), ("cluster2", "kind-ckaquest-lab")):
        subprocess.run(["kubectl", "config", "set-context", name, f"--cluster={kind_ctx}", f"--user={kind_ctx}"],
                       capture_output=True)


def conflicts(numbers):
    seen = {}
    for n in numbers:
        key = TOUCHES.get(n)
        if key and key in seen:
            return f"levels {seen[key]} and {n} both touch {key}"
        if key:
            seen[key] = n
    return None


def random_set(levels):
    by_domain = {}
    for n, d in levels.items():
        if n in EXCLUDED:
            continue
        m = load_mission(d)
        if m.get("exam") and m.get("domain") in DOMAIN_COUNTS:
            by_domain.setdefault(m["domain"], []).append(n)
    for _ in range(200):
        picked = []
        for dom, count in DOMAIN_COUNTS.items():
            picked += random.sample(by_domain[dom], min(count, len(by_domain[dom])))
        if not conflicts(picked):
            return {"name": "random", "description": "Random set with exam domain weights",
                    "minutes": 120, "tasks": [{"level": n} for n in picked]}
    raise SystemExit("could not build a conflict-free random set")


def load_set(name, levels):
    if name == "random":
        return random_set(levels)
    path = Path(name) if name.endswith(".yaml") else SETS / f"{name}.yaml"
    if not path.exists():
        raise SystemExit(f"no exam set '{name}'. Try: exam.sh list")
    with open(path) as f:
        return yaml.safe_load(f)


def assign_weights(tasks, missions):
    """Tasks without a weight share their domain's exam percentage."""
    per_domain = {}
    for t in tasks:
        per_domain.setdefault(missions[t["level"]].get("domain"), []).append(t)
    for dom, ts in per_domain.items():
        for t in ts:
            t.setdefault("weight", round(DOMAIN_WEIGHTS.get(dom, 10) / len(ts), 1))


def cmd_list():
    table = Table(title="Mock exams")
    table.add_column("Set"); table.add_column("Tasks"); table.add_column("Description")
    for p in sorted(SETS.glob("*.yaml")):
        s = yaml.safe_load(p.read_text())
        table.add_row(p.stem, str(len(s["tasks"])), s.get("description", ""))
    table.add_row("random", "17", "New set from the whole bank, exam domain weights")
    console.print(table)


def cmd_start(name):
    if load_state() and not load_state().get("ended"):
        raise SystemExit("an exam is running. Grade it (exam.sh grade) and end it (exam.sh end) first.")
    levels = all_levels()
    exam_set = load_set(name, levels)
    numbers = [t["level"] for t in exam_set["tasks"]]
    problem = conflicts(numbers)
    if problem:
        raise SystemExit(f"set {name} is not valid: {problem}")
    missions = {n: load_mission(levels[n]) for n in numbers}
    assign_weights(exam_set["tasks"], missions)
    ensure_contexts()

    console.print(Panel(f"[bold]Setting up {len(numbers)} tasks[/bold]. This takes a few minutes. The timer starts after setup.",
                        border_style="cyan"))
    for addon in sorted({a for m in missions.values() for a in m.get("requires", [])}):
        console.print(f"  [dim]add-on {addon}[/dim]")
        subprocess.run([str(CQ_ROOT / "bin" / "cq-cluster"), "addon", addon], capture_output=True)
    order = sorted(range(len(numbers)), key=lambda i: numbers[i] in DISRUPTIVE)
    for i in order:
        n = numbers[i]
        d, m = levels[n], missions[n]
        console.print(f"  [dim]task {i + 1}: {m['name']}[/dim]")
        run(d, "cleanup.sh", m)
        ns = m.get("namespace", "ckaquest")
        if ns not in PROTECTED:
            subprocess.run(["kubectl", "delete", "ns", ns, "--ignore-not-found", "--timeout=120s"], capture_output=True)
        subprocess.run(["kubectl", "create", "ns", ns], capture_output=True)
        r = run(d, "setup.sh", m)
        if (r is None or r.returncode == 0) and (d / "broken.yaml").exists():
            r = subprocess.run(["kubectl", "apply", "-f", str(d / "broken.yaml")], capture_output=True, text=True)
        if r is not None and r.returncode != 0:
            console.print(f"[red]  setup of task {i + 1} failed:[/red] {(r.stderr or r.stdout)[-300:]}")
    state = {
        "set": exam_set.get("name", name), "started": time.time(), "minutes": exam_set.get("minutes", 120),
        "tasks": [{"n": i + 1, "level": n, "path": str(levels[n].relative_to(CQ_ROOT)), "weight": t["weight"],
                   "domain": missions[n].get("domain"), "flag": False} for i, (n, t) in
                  enumerate(zip(numbers, exam_set["tasks"]))],
    }
    save_state(state)
    console.print(Panel("[bold green]Exam started.[/bold green] 120 minutes.\n"
                        "Work in your terminal with `source env.sh`. Use the context each task names.\n"
                        "`exam.sh` lists tasks, `exam.sh task 3` shows one, `exam.sh grade` when you are done.",
                        border_style="green"))
    cmd_tasks()


def need_state():
    s = load_state()
    if not s:
        raise SystemExit("no exam running. exam.sh start <set>")
    return s


def time_left(s):
    end = s["started"] + s["minutes"] * 60
    return max(0, int(end - (s.get("graded_at") or time.time())))


def fmt(sec):
    return f"{sec // 60:3d}:{sec % 60:02d}"


def cmd_tasks():
    s = need_state()
    table = Table(title=f"Exam {s['set']}  |  time left {fmt(time_left(s))}")
    for col in ("#", "Weight", "Domain", "Task", "Flag"):
        table.add_column(col)
    for t in s["tasks"]:
        m = load_mission(CQ_ROOT / t["path"])
        table.add_row(str(t["n"]), f"{t['weight']}%", t["domain"] or "", m["name"], "🚩" if t["flag"] else "")
    console.print(table)


def get_task(s, n):
    for t in s["tasks"]:
        if t["n"] == n:
            return t
    raise SystemExit(f"no task {n}")


def cmd_task(n):
    s = need_state()
    t = get_task(s, n)
    m = load_mission(CQ_ROOT / t["path"])
    body = exam_text(m.get("task") or m.get("description", ""))
    docs = "\n".join(f"- {d}" for d in m.get("docs", []))
    console.print(Panel(Markdown(body + (f"\n\n**Docs**\n\n{docs}" if docs else "")),
                        title=f"Task {n}  ({t['weight']}%, {t['domain']})", border_style="magenta"))
    console.print(f"[dim]time left {fmt(time_left(s))}[/dim]")


def cmd_flag(n):
    s = need_state()
    t = get_task(s, n)
    t["flag"] = not t["flag"]
    save_state(s)
    cmd_tasks()


def score_output(out):
    m = re.search(r"SCORE (\d+)/(\d+)", out or "")
    return (int(m.group(1)), int(m.group(2))) if m else (0, 1)


def cmd_grade():
    s = need_state()
    if not s.get("graded_at"):
        s["graded_at"] = time.time()
    console.print("[yellow]Grading every task...[/yellow]")
    total, by_domain = 0.0, {}
    table = Table(title=f"Result: exam {s['set']}")
    for col in ("#", "Task", "Domain", "Checks", "Points"):
        table.add_column(col)
    for t in s["tasks"]:
        d = CQ_ROOT / t["path"]
        m = load_mission(d)
        try:
            r = run(d, "validate.sh", m, timeout=300)
            got, of = score_output(r.stdout if r else "")
            t["output"] = r.stdout if r else ""
        except subprocess.TimeoutExpired:
            got, of = 0, 1
            t["output"] = "validation timed out"
        pts = t["weight"] * got / of
        t["points"] = round(pts, 2)
        total += pts
        dom = by_domain.setdefault(t["domain"], [0.0, 0.0])
        dom[0] += pts; dom[1] += t["weight"]
        table.add_row(str(t["n"]), m["name"], t["domain"] or "", f"{got}/{of}", f"{pts:.1f} / {t['weight']}")
    max_total = sum(t["weight"] for t in s["tasks"])
    pct = round(100 * total / max_total, 1) if max_total else 0
    s["score"] = pct
    save_state(s)
    console.print(table)
    dt = Table(title="By domain")
    dt.add_column("Domain"); dt.add_column("Score")
    for dom, (got, of) in by_domain.items():
        dt.add_row(dom or "", f"{100 * got / of:.0f}%")
    console.print(dt)
    used = int(s["graded_at"] - s["started"])
    verdict = "[bold green]PASS[/bold green]" if pct >= PASS_MARK else "[bold red]FAIL[/bold red]"
    console.print(Panel(f"{verdict}  {pct}%  (pass mark {PASS_MARK}%)  time used {used // 60} min", border_style="cyan"))
    hist = json.loads(HISTORY.read_text()) if HISTORY.exists() else []
    hist.append({"set": s["set"], "date": datetime.now().isoformat(timespec="minutes"), "score": pct,
                 "minutes": used // 60, "domains": {k: round(100 * v[0] / v[1]) for k, v in by_domain.items()}})
    HISTORY.write_text(json.dumps(hist, indent=2))
    console.print("[dim]exam.sh review shows the solutions. exam.sh end cleans up.[/dim]")


def cmd_review():
    s = need_state()
    if not s.get("graded_at"):
        raise SystemExit("grade first: exam.sh grade")
    for t in s["tasks"]:
        d = CQ_ROOT / t["path"]
        m = load_mission(d)
        console.rule(f"Task {t['n']}: {m['name']}  ({t.get('points', 0)} / {t['weight']})")
        console.print(t.get("output", ""))
        if (d / "solution.md").exists():
            console.print(Markdown(exam_text((d / "solution.md").read_text())))


def cmd_end():
    s = need_state()
    if not s.get("graded_at") and not os.environ.get("CQ_FORCE"):
        raise SystemExit("grade first (exam.sh grade), or CQ_FORCE=1 exam.sh end to drop it")
    console.print("[yellow]Cleaning up...[/yellow]")
    for t in reversed(s["tasks"]):
        d = CQ_ROOT / t["path"]
        m = load_mission(d)
        run(d, "cleanup.sh", m)
        ns = m.get("namespace", "ckaquest")
        if ns not in PROTECTED:
            subprocess.run(["kubectl", "delete", "ns", ns, "--ignore-not-found", "--wait=false"], capture_output=True)
    s["ended"] = True
    save_state(s)
    STATE.rename(EXAM_DIR / f"exam-{int(s['started'])}.json")
    console.print("[green]Done.[/green]")


def cmd_history():
    hist = json.loads(HISTORY.read_text()) if HISTORY.exists() else []
    table = Table(title="Exam history")
    for col in ("Date", "Set", "Score", "Minutes", "Weakest domain"):
        table.add_column(col)
    for h in hist:
        weakest = min(h["domains"].items(), key=lambda kv: kv[1])[0] if h["domains"] else ""
        table.add_row(h["date"], h["set"], f"{h['score']}%", str(h["minutes"]), weakest)
    console.print(table)


def main(argv):
    cmd = argv[0] if argv else "tasks"
    arg = argv[1] if len(argv) > 1 else None
    if cmd == "list":
        cmd_list()
    elif cmd == "start":
        cmd_start(arg or "random")
    elif cmd == "tasks":
        cmd_tasks()
    elif cmd == "task" and arg:
        cmd_task(int(arg))
    elif cmd == "flag" and arg:
        cmd_flag(int(arg))
    elif cmd == "time":
        console.print(fmt(time_left(need_state())))
    elif cmd == "grade":
        cmd_grade()
    elif cmd == "review":
        cmd_review()
    elif cmd == "end":
        cmd_end()
    elif cmd == "history":
        cmd_history()
    else:
        console.print(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
