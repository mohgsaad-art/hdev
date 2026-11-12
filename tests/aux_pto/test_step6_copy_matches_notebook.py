"""The reference_copy aux formula and PTO loop are COPIES.  This test runs the REAL notebook consumption_engine and compares, so the copies
cannot drift from Bob's code (the 'gate test that compares hard-coded numbers' pitfall of PRs #21-#27)."""
import numpy as np
import pytest

import reference_copy as RC
from _load_notebook import NS
from _scenarios import build_route, VPTOEL_T, VPTOEL_W
from _ce import call_ce

pto = NS["pto_engine"]


def test_aux_row_current_equals_notebook_P_aux_row():
    r = build_route([500, 500, 500], [10, 25, 20, 10])
    is_on, start, s1, d1 = pto(r["stop_wp"], [0, 1, 0, 0.0], VPTOEL_T, VPTOEL_W, [0.0], [0.0], 1.0, 1.0)
    out = call_ce(r, ES=1000.0, PS=200.0, HVAC=250.0, SP=23.0, cond=600.0, PTO_always_on=50.0, pto_1s=s1, pto_on_col=is_on, pto_start_col=start)
    row, active = RC.consumption_step6_current_loop(r["S"], r["V"], r["wp_s"], is_on, start, s1)
    mine = RC.aux_row_current(r["V"], active, 1000.0, 200.0, 250.0, 23.0, 600.0, 50.0, row)
    assert np.allclose(out[2], mine)


def test_new_variant_reproduces_old_loop_for_the_stop_profile():
    r = build_route([500, 500, 500], [10, 25, 30, 10])
    is_on, start, s1, d1 = pto(r["stop_wp"], [0, 1, 1, 0.0], VPTOEL_T, VPTOEL_W, [0.0], [0.0], 1.0, 1.0)
    old, _ = RC.consumption_step6_current_loop(r["S"], r["V"], r["wp_s"], is_on, start, s1)
    new, sa, da, ev = RC.consumption_step6_v_pto1nov(r["S"], r["V"], r["wp_s"], r["stop_wp"], is_on, start, s1, d1, M=r["M"])
    assert np.allclose(old, new) and da.sum() == 0 and sa.sum() == 46
