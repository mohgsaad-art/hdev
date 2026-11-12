"""Gate 1 (environment) and Gate 2 (code of record vs src copy).

Gate 1 runs docs/research/drag-default-test-2026-11/run_steps.py UNCHANGED (needs VECTO_SRC=<VECTO checkout with 'Generic Vehicles'>,
default /projects/sandbox/vecto-src) and reads its step3_kwh_per_km.csv.
Gate 3 (VECTO identity) is written by run_part_c.py (partC_gate3_identity.csv).

Run:  VECTO_SRC=/path/to/VECTO python run_gates_1_2.py
"""
import csv
import difflib
import os
import re
import subprocess
import sys

from _common import *

TARGET = {"RegionalDelivery": 0.9749, "UrbanDelivery": 0.8502}
TOL = 0.0005


def gate1():
    d = os.path.join(REPO, "docs", "research", "drag-default-test-2026-11")
    env = dict(os.environ)
    env.setdefault("VECTO_SRC", "/projects/sandbox/vecto-src")
    p = subprocess.run([sys.executable, "run_steps.py"], cwd=d, env=env, capture_output=True, text=True)
    rows = list(csv.DictReader(open(os.path.join(d, "step3_kwh_per_km.csv"))))
    res = []
    for cyc, tgt in TARGET.items():
        r = [x for x in rows if x["cycle"] == cyc and x["load"] == "reference" and x["chain"] == "S" and x["variant"].startswith("V1")][0]
        v = float(r["kwh_km"])
        res.append(dict(gate="1", check=f"Chain S V1 reference {cyc} kWh/km", expected=tgt, got=v, tol=TOL, passed=abs(v - tgt) <= TOL,
                        run_steps_returncode=p.returncode))
    return res


def gate2():
    nb_src = cell_source_force()
    src = open(os.path.join(REPO, "src", "engine", "force_engine.py"), encoding="utf-8").read()

    def body(s):
        i = s.index("def force_engine")
        return [l.rstrip() for l in s[i:].splitlines() if l.strip()]
    a, b = body(nb_src), body(src)
    diff = [l for l in difflib.unified_diff(a, b, "notebook", "src", lineterm="", n=0) if not l.startswith(("---", "+++", "@@"))]
    return [dict(gate="2", check="force_engine body: notebook (code of record) vs src/engine/force_engine.py", expected="identical statements",
                 got="identical" if not diff else "; ".join(diff), tol="", passed=not diff, run_steps_returncode="")]


def cell_source_force():
    from _load_notebook import cell_source
    return cell_source(8)


if __name__ == "__main__":
    write_csv("gates_1_2.csv", gate1() + gate2())
