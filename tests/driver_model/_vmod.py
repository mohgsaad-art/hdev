"""Loader for VECTO .vmod modal-result files and the .vsum summary.

The .vmod first line is a '# VECTO-RC ...' comment; line 2 is the CSV header.
DriverAction codes (Driver.cs line 50, v5.1.3): Halt=0, Roll=2, Coast=4,
Accelerate=6, Brake=-5.
"""
import csv
import os

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(_HERE))
VECTO_RUNS = os.path.join(_REPO, "docs", "research", "vecto")

# VECTO DriverAction -> HDEV mode (verified mapping, review Q12).
# Note: VECTO has no "cruise" code; Roll and Coast both map to HDEV coast (3).
VECTO_ACTION_TO_MODE = {0: 0, 2: 3, 6: 1, 4: 3, -5: 4}
VECTO_ACTION_NAME = {0: "Halt", 2: "Roll", 4: "Coast", 6: "Accelerate", -5: "Brake"}


def load_vmod(path):
    """Return a dict of numpy columns keyed by the clean header name.

    Handles the leading '#' comment line. DriverAction is kept as int.
    """
    with open(path, encoding="utf-8-sig", newline="") as fh:
        first = fh.readline()
        if not first.lstrip().startswith("#"):
            fh.seek(0)
        reader = csv.reader(fh)
        header = [h.strip().lstrip("\ufeff") for h in next(reader)]
        rows = [r for r in reader if r and not r[0].startswith("#")]
    cols = {}
    for i, name in enumerate(header):
        vals = []
        for r in rows:
            if i >= len(r):
                vals.append(np.nan)
                continue
            s = r[i].strip()
            try:
                vals.append(float(s))
            except ValueError:
                vals.append(np.nan)
        cols[name] = np.array(vals)
    return cols


def col(cols, *candidates):
    """Return the first column whose cleaned name matches one of candidates."""
    for cand in candidates:
        for k in cols:
            if k == cand or k.split(" [")[0].strip() == cand:
                return cols[k]
    raise KeyError(f"none of {candidates} in {list(cols)[:8]}...")


def run_files():
    """Map a short label to the .vmod path, for whatever is present."""
    out = {}
    if not os.path.isdir(VECTO_RUNS):
        return out
    for fn in sorted(os.listdir(VECTO_RUNS)):
        if fn.lower().endswith(".vmod"):
            out[fn[:-5]] = os.path.join(VECTO_RUNS, fn)
    return out
