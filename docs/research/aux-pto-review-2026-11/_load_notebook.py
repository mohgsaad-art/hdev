"""Load Bob's code-of-record notebook functions, unchanged.

Reads the .ipynb JSON, takes the code cells only, skips cell 0 (imports torch,
gymnasium, requests ... not needed), and exec's the rest in ONE namespace that
starts with `import math, bisect; import numpy as np`. No cell text is changed.

Usage:  from _load_notebook import NS, load
        P_aux = NS["P_aux"]
Run directly to print the function names loaded.
"""
import json
import os
import hashlib

_HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
NB_PATH = os.path.join(REPO, "docs", "research", "inputs",
                       "HDEV_NEW_code_of_record_2026-11-12.ipynb")


def load(path=NB_PATH):
    with open(path, encoding="utf-8") as fh:
        nb = json.load(fh)
    ns = {}
    exec("import math, bisect\nimport numpy as np", ns)
    code_cells = [(i, "".join(c["source"])) for i, c in enumerate(nb["cells"])
                  if c["cell_type"] == "code"]
    for i, src in code_cells:
        if i == 0:
            continue  # imports torch/gymnasium/requests: not needed, not installed
        exec(compile(src, f"<notebook cell {i}>", "exec"), ns)
    return ns


def cell_source(idx, path=NB_PATH):
    with open(path, encoding="utf-8") as fh:
        nb = json.load(fh)
    return "".join(nb["cells"][idx]["source"])


def notebook_sha256(path=NB_PATH):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


NS = load()

if __name__ == "__main__":
    import types
    names = sorted(k for k, v in NS.items() if isinstance(v, types.FunctionType))
    print("notebook:", os.path.relpath(NB_PATH, REPO))
    print("sha256:", notebook_sha256())
    print("functions loaded:", names)
