"""Path set-up for the aux/PTO review tests.  The notebook is loaded unchanged by
docs/research/aux-pto-review-2026-11/_load_notebook.py, so these tests exercise Bob's exact code of record (12 Nov 2026)."""
import os
import sys

_REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_REVIEW = os.path.join(_REPO, "docs", "research", "aux-pto-review-2026-11")
for p in (_REVIEW, _REPO):
    if p not in sys.path:
        sys.path.insert(0, p)
os.environ.setdefault("VECTO_SRC", "/projects/sandbox/vecto-src")
