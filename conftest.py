# STATUS: NEW (PR 1, Bob to review). Puts the repo root on sys.path so tests import the packages as
# src.registry / src.validate when pytest runs from the repo root.
import os
import sys

_ROOT = os.path.dirname(os.path.abspath(__file__))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
