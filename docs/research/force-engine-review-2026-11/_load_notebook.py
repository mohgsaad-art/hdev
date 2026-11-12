"""Load Bob's code of record (12 Nov 2026 notebook) without changing any cell text.

Rules (prompt section 0.3): code cells only, skip cell 0 (torch/gymnasium/requests imports),
exec the rest in ONE namespace that starts with `import math, bisect; import numpy as np`.
"""
import json
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
NOTEBOOK = os.path.join(REPO, "docs", "research", "inputs",
                        "HDEV_NEW_code_of_record_2026-11-12.ipynb")


def load(verbose=False):
    nb = json.load(open(NOTEBOOK, encoding="utf-8"))
    ns = {"__name__": "hdev_notebook"}
    exec("import math, bisect; import numpy as np", ns)
    for i, c in enumerate(nb["cells"]):
        if c["cell_type"] != "code" or i == 0:
            continue
        exec(compile("".join(c["source"]), f"<notebook cell {i}>", "exec"), ns)
    if verbose:
        fns = sorted(k for k, v in ns.items() if callable(v) and not k.startswith("__")
                     and getattr(v, "__module__", None) in (None, "hdev_notebook") and not isinstance(v, type)
                     and k not in ("math", "bisect", "np"))
        print("functions loaded from notebook:", ", ".join(fns))
    return ns


def cell_source(i):
    nb = json.load(open(NOTEBOOK, encoding="utf-8"))
    return "".join(nb["cells"][i]["source"])


if __name__ == "__main__":
    load(verbose=True)
