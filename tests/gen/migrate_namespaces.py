"""One-off: move base levels 1 to 50 from the shared ckaquest namespace to their own namespace.

Replaces namespace uses of the word "ckaquest" inside each level folder. Leaves alone:
kind-ckaquest (context), ckaquest-worker (nodes), ~/ckaquest-work, ~/.ckaquest.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPECIAL = {10: "team-a", 44: "netpol-db", 48: None, 1: "pods-lab", 2: "deploy-lab"}
WORD = re.compile(r"(?<![\w/.-])ckaquest(?![\w/-])")
DNS = re.compile(r"\.ckaquest\.svc")

changed = 0
for d in sorted((ROOT / "worlds").glob("world-[1-5]-*/level-*")):
    n = int(re.search(r"level-(\d+)", d.name).group(1))
    ns = SPECIAL.get(n, d.name.split("-", 2)[2])
    if ns is None:
        continue
    for f in d.iterdir():
        if f.suffix not in (".yaml", ".sh", ".md", ".txt"):
            continue
        s = f.read_text()
        t = DNS.sub(f".{ns}.svc", WORD.sub(ns, s))
        if f.name == "mission.yaml" and not re.search(r"^namespace:", t, re.M):
            t = t.rstrip("\n") + f"\nnamespace: {ns}\n"
        if t != s:
            f.write_text(t)
            changed += 1
    print(f"{d.name:40s} {ns}")
print("files changed:", changed)
