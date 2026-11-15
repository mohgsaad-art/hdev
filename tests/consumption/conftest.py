"""pytest set-up for the consumption-engine tests (13 Nov 2026).  Test-only; no engine code is changed.
All tests call the function loaded from Bob's notebook (code of record, 13 Nov) or a named variant in
docs/research/consumption-review-2026-11/reference_copy.py."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
REV = os.path.join(REPO, "docs", "research", "consumption-review-2026-11")
for p in (REV, REPO):
    if p not in sys.path:
        sys.path.insert(0, p)
os.environ.setdefault("MPLCONFIGDIR", "/tmp/mpl")
os.environ.setdefault("VECTO_SRC", os.path.join(os.path.dirname(REPO), "vecto-src"))
