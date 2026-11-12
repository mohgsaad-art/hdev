"""Load Bob's notebook code (code of record 12 Nov 2026) into one namespace.

Rules (Kiro prompt 0.4): read the .ipynb JSON, take CODE cells only, skip cell 0
(heavy imports), exec the rest in one namespace that starts with
`import math, bisect; import numpy as np`. No cell text is changed.

Usage:  from _load_notebook import NS, cell_source
        NS["HVAC_thermal"](...)
"""
import json
import os
import types

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
NOTEBOOK = os.path.join(_REPO, "docs", "research", "inputs",
                        "HDEV_NEW_code_of_record_2026-11-12.ipynb")


def _cells():
    with open(NOTEBOOK, encoding="utf-8") as f:
        nb = json.load(f)
    return nb["cells"]


def cell_source(idx):
    """Exact source text of notebook cell `idx` (joined, unchanged)."""
    return "".join(_cells()[idx]["source"])


def load():
    ns = {"__name__": "hdev_notebook"}
    exec("import math, bisect\nimport numpy as np", ns)
    loaded = []
    for i, c in enumerate(_cells()):
        if c["cell_type"] != "code" or i == 0:
            continue
        src = "".join(c["source"])
        exec(compile(src, f"<notebook cell {i}>", "exec"), ns)
    for k, v in ns.items():
        if isinstance(v, types.FunctionType):
            loaded.append(k)
    return ns, loaded


NS, FUNCTIONS = load()

if __name__ == "__main__":
    print("notebook:", NOTEBOOK)
    print("functions loaded:", ", ".join(sorted(FUNCTIONS)))
