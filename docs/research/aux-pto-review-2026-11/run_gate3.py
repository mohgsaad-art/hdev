"""Gate 3: the notebook is the code of record.  Compare (a) the notebook cells with the code blocks in the prompt's Appendix 1 and
(b) with src/engine/ (what exists there).  Writes gate3_differences.csv.  Run: python run_gate3.py"""
import difflib
import os
import re
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _load_notebook import cell_source, REPO, NB_PATH  # noqa: E402

PROMPT = os.path.join(REPO, "docs", "research", "inputs", "kiro-prompt-aux-pto-review-2026-11-12.md")


def blocks(text):
    return re.findall(r"```python\n(.*?)```", text, flags=re.S)


def norm(s):
    return [re.sub(r"\s+", " ", l).strip() for l in s.splitlines() if l.strip()]


def diff_rows(label, a, b, a_name, b_name):
    rows = []
    sm = difflib.SequenceMatcher(None, a, b)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag != "equal":
            rows.append(dict(item=label, kind=tag, **{a_name: " | ".join(a[i1:i2])[:300], b_name: " | ".join(b[j1:j2])[:300]}))
    return rows


def main():
    pb = blocks(open(PROMPT, encoding="utf-8").read())
    rows = []
    # (a) Appendix 1.1 -1.4 vs notebook
    pairs = [("P_aux (1.1)", 9), ("SP_power_helper (1.2)", 10), ("pto_engine (1.3)", 14)]
    for k, (label, cell) in enumerate(pairs):
        app = next(b for b in pb if re.search(r"def (P_aux|SP_power_helper|pto_engine)\(", b) and label.split(" ")[0].lower() in b.lower().split("def")[1][:30])
        nb = cell_source(cell)
        d = diff_rows(label, norm(app), norm(nb), "appendix", "notebook")
        rows += d or [dict(item=label, kind="IDENTICAL (whitespace-normalised)", appendix="", notebook="")]
    # 1.4: steps 6-7 only (from '# --- 6.' to the return)
    app14 = next(b for b in pb if "def consumption_engine" in b)
    nb16 = cell_source(16)
    cut = lambda s: s[s.index("# --- 6."):s.index("return P_wheel")]
    d = diff_rows("consumption_engine steps 6-7 (1.4)", norm(cut(app14)), norm(cut(nb16)), "appendix", "notebook")
    rows += d or [dict(item="consumption_engine steps 6-7 (1.4)", kind="IDENTICAL (whitespace-normalised)", appendix="", notebook="")]
    # (b) src/engine
    src_dir = os.path.join(REPO, "src", "engine")
    src_files = sorted(os.listdir(src_dir))
    rows.append(dict(item="src/engine contents", kind="info", appendix="", notebook=", ".join(f for f in src_files if f.endswith(".py"))))
    pa = open(os.path.join(src_dir, "p_aux.py")).read()
    rows += [
        dict(item="src/engine/p_aux.py", kind="DIFFERENT FUNCTION", appendix="def p_aux(P_ES, P_HVAC, P_PS, P_SP, P_Cond, moving, motor_on, aux_weather_fn=None)",
             notebook="def P_aux(ES_power, PS_power, HVAC_power, SP_power, cond_power, PTO_always_on, ES_alteff=0.7, ..., PTO_eff=1.0)"),
        dict(item="src/engine/p_aux.py", kind="no efficiency factors", appendix="returns P_ES + P_HVAC + P_PS + P_SP*moving + P_Cond*motor_on (row array)", notebook="returns six electric-W values; factors 0.7/1.0/1.25/0.7/1.0 and PTO_eff inside"),
        dict(item="src/engine/p_aux.py", kind="no PTO, no checks on sign", appendix="None-check only (blank cell)", notebook="negative / efficiency checks (PTO ones missing)"),
        dict(item="src/engine/p_aux.py", kind="motor_on per row", appendix="Cond * motor_on (per-row bool given by caller)", notebook="Cond * (moving | pto_active) inside consumption_engine step 6"),
        dict(item="src/engine pto_engine", kind="NOT PRESENT", appendix="(no pto_engine in src/engine)", notebook="notebook cell 14 is the only pto_engine"),
        dict(item="src/engine/consumption.py", kind="different/older", appendix="consumption(P_wheel, eta_drive=0.95, eta_regen=0.95, eta_dcdc=0.98, P_aux=0, dt_s=1.0)",
             notebook="consumption_engine(...) steps 1-7; DC/DC = 1.0 (no factor)"),
    ]
    df = pd.DataFrame(rows)
    p = os.path.join(HERE, "gate3_differences.csv")
    df.to_csv(p, index=False)
    print(df[["item", "kind"]].to_string(index=False))
    print("file written:", os.path.relpath(p, REPO))


if __name__ == "__main__":
    main()
