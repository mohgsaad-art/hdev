"""Gate 2: are the 3 functions in notebook cells 11-13 identical to Appendix 1 of the prompt?
Compares byte-for-byte after (a) joining the notebook cell, (b) stripping trailing whitespace per line
and the final newline (markdown copy-paste may change those)."""
import difflib
from _load_notebook import cell_source
import appendix1_prompt_text as A

PAIRS = [(11, "HVAC_THERMAL"), (12, "SSM_TOTAL_W"), (13, "CLIMATE_LOOKUP")]
def norm(s): return "\n".join(l.rstrip() for l in s.strip("\n").split("\n"))
ok_all = True
for idx, name in PAIRS:
    nb, ap = cell_source(idx), getattr(A, name)
    exact = nb == ap
    same = norm(nb) == norm(ap)
    print(f"cell {idx} {name}: byte-identical={exact}  identical-after-trailing-ws-strip={same}")
    if not same:
        ok_all = False
        for l in difflib.unified_diff(norm(ap).split("\n"), norm(nb).split("\n"), "prompt", "notebook", lineterm=""):
            print("   ", l)
    elif not exact:
        print("    (differences only in trailing whitespace / final newline)")
print("GATE 2:", "PASS" if ok_all else "DIFFERENCES FOUND")
