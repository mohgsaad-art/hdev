import os, sys
REVIEW = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "docs", "research", "hvac-review-2026-11")
REVIEW = os.path.abspath(REVIEW)
if REVIEW not in sys.path:
    sys.path.insert(0, REVIEW)
