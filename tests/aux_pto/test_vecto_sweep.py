"""Part B.2 + Gate 2: HDEV (notebook SP_power_helper + P_aux) vs the independent re-implementation of the VECTO C#, over every
group x mission x technology a PEV lorry can have.  Also Gate 2 against the E2 .vmod files."""
import itertools
import os

import numpy as np
import pandas as pd
import pytest

import run_part_b_sweep as SW
import vecto_aux_reimpl as V


@pytest.fixture(scope="module")
def parser():
    return SW.HdevParser()


def test_gate2_e2_vs_vmod(parser):
    written = []
    df = SW.gate2(parser, written)
    # 0.011 W is the 4-decimal-kW print resolution of the .vmod (23.009 W prints as 0.0230 kW)
    assert df["diff_W"].abs().max() < 0.02
    assert df[df.aux.isin(["ES", "HVAC", "PS", "COND"])]["diff_W"].abs().max() < 1e-6


def test_every_valid_combination_matches_vecto_reimplementation(parser):
    seg = SW.segment_groups()
    es_t = [r[0] for r in parser.es_rows]
    ps_t = [r[0] for r in parser.ps_rows if r[SW._col(parser.ps_h, "pev")] == "1"]
    sp_t = [r[0] for r in parser.spt_rows if r[SW._col(parser.spt_h, "pev")] == "1"]
    n, worst = 0, 0.0
    for g, info in seg.items():
        for mission in V.MISSIONS:
            for n_ax in (1, 2, 3, 4):
                for sp in itertools.product(sp_t, repeat=n_ax):
                    for es, hv, ps in itertools.product(es_t, ["None", "Default"], ps_t):
                        try:
                            h = SW.hdev_total(parser, g, mission, es, hv, ps, sp)
                            v = SW.vecto_total(g, mission, es, hv, ps, sp)
                        except LookupError:
                            continue
                        n += 1
                        worst = max(worst, max(abs(h[k] - v[k]) for k in v))
    assert n > 60000 and worst < 1e-9


def test_hdev_and_vecto_agree_on_which_cells_are_empty(parser):
    seg = SW.segment_groups()
    for g in seg:
        for mission in V.MISSIONS:
            h = v = None
            try:
                parser.sp(g, mission, ["Full electric steering gear"])
            except LookupError as e:
                h = e
            try:
                V.sp_electric_W(g, mission, ["Full electric steering gear"])
            except LookupError as e:
                v = e
            assert (h is None) == (v is None), (g, mission)


def test_vecto_has_no_fifth_steered_axle_row():
    with pytest.raises(LookupError, match="steered axle number 5"):
        V.sp_electric_W("5", "Regional delivery", ["Full electric steering gear"] * 5)


def test_non_pev_technologies_are_rejected_by_vecto_reimplementation():
    with pytest.raises(LookupError, match="not applicable"):
        V.sp_electric_W("2", "Regional delivery", ["Fixed displacement"])
    with pytest.raises(LookupError, match="not applicable"):
        V.ps_electric_W("Regional delivery", "Small")


def test_municipal_mission_exists_only_for_groups_4_9_11():
    seg = SW.segment_groups()
    assert sorted(g for g, i in seg.items() if i["valid"] and "Municipal utility" in i["missions"]) == ["11", "4", "9"]


def test_hvac_default_group_5_and_10_municipal_zero_is_never_looked_up():
    """Groups 5 and 10 have no Municipal utility mission in SegmentTable.csv, so the explicit 0 W cell is never used."""
    seg = SW.segment_groups()
    assert "Municipal utility" not in seg["5"]["missions"] and "Municipal utility" not in seg["10"]["missions"]
    assert V.TABLES["hvac"][("municipal utility", "Default", "5")] == 0.0
    assert V.TABLES["hvac"][("municipal utility", "Default", "10")] == 0.0


def test_ps_el_column_is_not_always_0_7_times_mech_column():
    """The AMS rows: *_el is far from 0.7 x mech (e.g. 'Small + AMS + elec. driven' 675 vs 0.7 x 357 = 250)."""
    rec = V.TABLES["ps"]["Small + AMS + elec. driven"]
    assert rec["el"]["long haul"] == 675.0 and rec["mech"]["long haul"] * 0.7 == pytest.approx(249.9)
    rec2 = V.TABLES["ps"]["Small + elec. driven"]
    assert rec2["el"]["long haul"] == pytest.approx(rec2["mech"]["long haul"] * 0.7, abs=1.0)
