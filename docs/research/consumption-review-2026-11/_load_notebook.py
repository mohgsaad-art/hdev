"""Load Bob's notebook functions WITHOUT changing any cell text.

Reads the .ipynb JSON, takes code cells only, skips cell 0 (heavy imports: torch, gymnasium,
requests ...) and every cell that has no `def` (examples / plots), and exec()s the rest in one
namespace that starts with `import math, bisect; import numpy as np`.

Usage:  from _load_notebook import NS, load   ;  NS['consumption_engine'](...)
"""
import json
import os
import re
import sys

NOTEBOOK_DEFAULT = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "inputs",
    "HDEV_NEW_code_of_record_2026-11-13.ipynb")


REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
NB_PATH = NOTEBOOK_DEFAULT


def cell_sources(path=NOTEBOOK_DEFAULT):
    nb = json.load(open(path))
    return [(i, "".join(c["source"])) for i, c in enumerate(nb["cells"]) if c["cell_type"] == "code"]


def load(path=NOTEBOOK_DEFAULT, verbose=False):
    ns = {}
    exec("import math, bisect\nimport numpy as np", ns)
    loaded, skipped = [], []
    for i, src in cell_sources(path):
        if i == 0:
            skipped.append((i, "heavy imports (torch, gymnasium, requests ...)"))
            continue
        if not re.search(r"^def \w+", src, re.M):
            skipped.append((i, "no function definition (example / plot)"))
            continue
        before = set(ns)
        exec(compile(src, f"<notebook cell {i}>", "exec"), ns)
        loaded.append((i, sorted(k for k in set(ns) - before if callable(ns[k]))))
    if verbose:
        for i, names in loaded:
            print(f"cell {i}: {', '.join(names)}")
        for i, why in skipped:
            print(f"cell {i} skipped: {why}")
    return ns


NS = load()

if __name__ == "__main__":
    load(verbose=True)
    print("functions in NS:", sorted(k for k, v in NS.items() if callable(v) and not k.startswith("_")
                                    and getattr(v, "__module__", None) is None))
