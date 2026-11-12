"""Part F: independent comparison of HDEV aux / PTO totals with published figures (only what was actually read).
Inputs that are missing are marked BLOCKED / NOT FOUND, never filled.  Deterministic.   Run: python run_part_f.py"""
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _rows import read_vmod, read_vdri, run_driver_e2, REPO  # noqa: E402
from _scenarios import VPTOEL_T, VPTOEL_W, VPTOEL_KWH  # noqa: E402
import reference_copy as RC  # noqa: E402
from _load_notebook import NS  # noqa: E402

rows = []

# ---- F1: aux share of battery-terminal energy in the VECTO E2 runs (VECTO is the reference, not validation) ----
for cyc, load in [("RegionalDelivery", "ReferenceLoad"), ("UrbanDelivery", "ReferenceLoad"), ("LongHaul", "ReferenceLoad")]:
    d = read_vmod(cyc, load)
    e_term = -d["P_REESS_T [kW]"].sum() / 3600.0              # net energy drawn at the battery terminals [kWh] (VECTO: discharge is negative); includes aux
    e_aux = d["P_aux_el [kW]"].sum() / 3600.0
    km = d["dist [m]"].iloc[-1] / 1000.0
    rows.append(dict(item=f"F1 VECTO E2 {cyc} {load}: aux energy share of battery-terminal energy", value=e_aux / e_term * 100, unit="%",
                     detail=f"aux {e_aux:.3f} kWh of {e_term:.2f} kWh over {km:.1f} km ({e_aux / km:.4f} kWh/km)", tag="[CALC] from .vmod P_aux_el, P_REESS_T",
                     compared_with="NOT FOUND: no measured aux share of a 12 t e-truck was read in full text (see Bob to fetch)"))

# ---- F2: MunicipalUtility, HDEV rows, VECTO generic refuse profile; E2 vehicle used only as a stand-in (ASSUMPTION) ----
cy = read_vdri("MunicipalUtility")
flag = cy["pto"] == 1
sf = cy["stop"].copy(); sf[flag] += 23
is_on, ps, s1, d1 = NS["pto_engine"](sf, flag.astype(float), VPTOEL_T, VPTOEL_W, [0.0], [0.0], 1.0, 1.0)
T, S, V, A, G, M = run_driver_e2(cy, "ReferenceLoad", stop_override=sf)
pto_row, sa, da, ev = RC.consumption_step6_v_pto1nov(S, V, cy["s"], sf, is_on, ps, s1, d1, M=M)
km = cy["s"][-1] / 1000.0
# aux with Urban E2 values (ASSUMPTION: group 2 has no Municipal mission; Urban values used, as in the drag-default test)
ES, PS, HV, SP, CD = 1000.0, 162.0, 187.5, 32.011, 550.0
aux = RC.aux_row_current(V, sa, ES, PS, HV, SP, CD, 0.0, np.zeros(len(T)))
e_pto = pto_row.sum() / 3.6e6
e_aux = aux.sum() / 3.6e6
rows += [
    dict(item="F2 HDEV Municipal (VECTO generic refuse profile): stop-PTO energy per PTO stop", value=VPTOEL_KWH, unit="kWh/stop", detail="5*8.42+4*33.69+14*25.92 kJ", tag="[VECTO] file + [CALC]", compared_with=""),
    dict(item="F2 HDEV Municipal: stop-PTO energy per km of route", value=e_pto / km, unit="kWh/km", detail=f"{e_pto:.3f} kWh / {km:.2f} km, 96 stops", tag="[TEST] run_part_d + [CALC]", compared_with=""),
    dict(item="F2 HDEV Municipal: aux (E2 Urban values, ASSUMPTION) energy per km, includes Cond during PTO", value=e_aux / km, unit="kWh/km", detail=f"{e_aux:.3f} kWh; route time {T[-1] + 1:.0f} s", tag="[ASSUMPTION] Urban aux + [CALC]", compared_with=""),
    dict(item="F2 HDEV Municipal: non-traction energy (PTO + aux) per km", value=(e_pto + e_aux) / km, unit="kWh/km", detail="", tag="[CALC]", compared_with=""),
]
# VTT numbers (page read in full: vttresearch.com project news 24.05.2023)
tot, drv = 2.3, 1.4
rows += [
    dict(item="F2 VTT/HSY e-refuse truck, winter pilot: total energy in refuse collection", value=tot, unit="kWh/km", detail="'approximately 2.3 kWh/km'", tag="[SOURCE] full page read, 24 May 2023; one truck, Helsinki region, Feb conditions", compared_with=""),
    dict(item="F2 VTT: driving part", value=drv, unit="kWh/km", detail="'most ... comes from driving (1.4 kWh/km)'", tag="[SOURCE]", compared_with=""),
    dict(item="F2 VTT: everything that is not driving (body hydraulics, cabin heating/demisting, 24 V ...)", value=tot - drv, unit="kWh/km", detail="2.3 - 1.4", tag="[CALC] on [SOURCE]", compared_with="HDEV non-traction above: boundaries differ (VTT includes cabin heat in winter and an electric-driven hydraulic pump)"),
    dict(item="F2 VTT: upper bound of non-driving energy per emptied container", value=(tot - drv) * 120.0 / 500.0, unit="kWh/container", detail="0.9 kWh/km x 120 km / 500 containers; page says 'more than five hundred containers' and 'over 120 km' so this is an upper bound", tag="[CALC] on [SOURCE]", compared_with=f"VECTO generic profile {VPTOEL_KWH:.3f} kWh per stop (one stop is not one container)"),
    dict(item="F2 spread: HDEV (VECTO profile) stop PTO / VTT non-driving per container bound", value=VPTOEL_KWH / ((tot - drv) * 120.0 / 500.0), unit="ratio", detail="< 1 means HDEV/VECTO profile is below the VTT all-in non-driving figure; NOT like-for-like", tag="[CALC]", compared_with="n=1 vehicle: this is a plausibility check, not validation"),
]
# ---- F3: items that cannot be computed ----
for what, why in [
    ("Concrete mixer drum kWh/hour", "BLOCKED: no sourced mixer vehicle set-up (mass, body, route) in the repo; Liebherr ETM sheet gives only drive rating 125 kW peak / 60 kW continuous [OEM], no consumption"),
    ("Refrigerated body kWh/hour", "BLOCKED: no ATP certificate (K, surface S) or measured TRU load; Carrier eCool sheet gives only 19 kW max continuous battery discharge [OEM]"),
    ("Measured standing aux power of a BEV truck (SP/Cond off at standstill in VECTO)", "NOT FOUND: no measured standing-aux figure was read in full text"),
    ("Measured Cond (battery/motor thermal management) power, summer and winter", "NOT FOUND in full text; Dollinger 2021 (battery heating ~4 %) lead could not be opened"),
]:
    rows.append(dict(item=f"F3 {what}", value=np.nan, unit="", detail=why, tag="BLOCKED / NOT FOUND", compared_with=""))
df = pd.DataFrame(rows)
p = os.path.join(HERE, "partF_validation.csv")
df.to_csv(p, index=False, float_format="%.5f")
pd.set_option("display.width", 230, "display.max_colwidth", 90)
print(df[["item", "value", "unit"]].to_string(index=False))
print("file written:", os.path.relpath(p, REPO))
